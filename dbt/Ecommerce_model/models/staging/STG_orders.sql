{{
    config(
        materialized='incremental',
        strategy='append',
        unique_key='order_sk',
        indexes = 
        [
            {"columns": ['order_sk'], 'unique': True}
        ]
    )
}}

with completed_orders as (
    select 
        distinct order_id,
        user_id,
        product_id,
        timestamp,
        quantity[1]::int,
        amount::numeric,
        payment_method,
        'Completed' as status,
        'supabase' as source,
        current_timestamp as created_at,
        current_timestamp as updated_at
    from {{ source('ecommerce_oltp', 'order_complete_response') }}
    where order_id is not null
    and user_id is not null
    and product_id is not null
    and timestamp is not null
    and quantity[1]::int >0
    and amount >0
    and payment_method is not null
),
failed_orders as (
    select 
        distinct order_id,
        user_id,
        product_id,
        timestamp,
        0 as quantity,
        0 as amount,
        payment_method,
        'Failed' as status,
        'supabase' as source,
        current_timestamp as created_at,
        current_timestamp as updated_at
    from {{ source('ecommerce_oltp', 'order_failed_response') }}
    where order_id is not null
    and user_id is not null
    and product_id is not null
    and timestamp is not null
    and payment_method is not null
),
purchase as (
    select 
        'mock_order_id' as order_id,
        user_id,
        product_id,
        timestamp,
        quantity[1]::int as quantity,
        amount::numeric as amount,
        payment_method,
        'Purchase' as status,
        'supabase' as source,
        current_timestamp as created_at,
        current_timestamp as updated_at,
        row_number() over (partition by timestamp order by timestamp desc) as rn
    from {{ source('ecommerce_oltp', 'purchase_response') }}
    where user_id is not null
    and product_id is not null
    and timestamp is not null
    and payment_method is not null
    and quantity[1]::int >0
    and amount >0

),
final as (
    select
        md5(order_id::text || source || status || timestamp || user_id::text || product_id::text) as order_sk,
        order_id::text,
        user_id::text,
        product_id::text,
        timestamp,
        quantity::int,
        amount::numeric,
        payment_method,
        status,
        source,
        created_at,
        updated_at
    from completed_orders
    union all
    select
        md5(order_id::text || source || status || timestamp || user_id::text || product_id::text) as order_sk,
        order_id::text,
        user_id::text,
        product_id::text,
        timestamp,
        quantity::int,
        amount::numeric,
        payment_method,
        status,
        source,
        created_at,
        updated_at
    from failed_orders
    union all
    select
        md5(order_id::text || source || status || timestamp || user_id::text || product_id::text) as order_sk,
        order_id::text,
        user_id::text,
        product_id::text,
        timestamp,
        quantity::int,
        amount::numeric,
        payment_method,
        status,
        source,
        created_at,
        updated_at
    from purchase
)

{% if is_incremental() %}
-- Incremental logic: Insert only new or updated rows
select * from final
where order_sk not in (select distinct order_sk from {{ this }})
{% else %}
-- Full refresh logic: Load all rows
select * from final
{% endif %}
