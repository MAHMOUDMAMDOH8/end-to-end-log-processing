{{
    config(
        materialized='incremental',
        strategy='append',
        unique_key='event_sk',
        indexes = 
        [
            {"columns": ['event_sk'], 'unique': True}
        ]
    )
}}

with completed_orders as (
    select 
        user_id,
        product_id,
        timestamp,
        event_type,
        session_id,
        device_type,
        geo_country,
        geo_city,
        'supabase' as source,
        current_timestamp as created_at,
        current_timestamp as updated_at
    from {{ source('ecommerce_oltp', 'order_complete_response') }}
    where order_id is not null
    and user_id is not null
    and product_id is not null
    and timestamp is not null
),
failed_orders as (
    select 
        user_id,
        product_id,
        timestamp,
        event_type,
        session_id,
        device_type,
        geo_country,
        geo_city,
        'supabase' as source,
        current_timestamp as created_at,
        current_timestamp as updated_at
    from {{ source('ecommerce_oltp', 'order_failed_response') }}
    where order_id is not null
    and user_id is not null
    and product_id is not null
    and timestamp is not null
),
purchase as (
    select 
        user_id,
        product_id,
        timestamp,
        event_type,
        session_id,
        device_type,
        geo_country,
        geo_city,
        'supabase' as source,
        current_timestamp as created_at,
        current_timestamp as updated_at
    from {{ source('ecommerce_oltp', 'purchase_response') }}
    where user_id is not null
    and product_id is not null
    and timestamp is not null
),
search_response as (
    select 
        user_id,
        product_id,
        timestamp,
        event_type,
        session_id,
        device_type,
        geo_country,
        geo_city,
        'supabase' as source,
        current_timestamp as created_at,
        current_timestamp as updated_at 
    from {{ source('ecommerce_oltp', 'search_response') }}
    where user_id is not null
    and product_id is not null
    and timestamp is not null
),
error_response as (
    select 
        user_id,
        product_id,
        timestamp,
        event_type,
        session_id,
        device_type,
        geo_country,
        geo_city,
        'supabase' as source,
        current_timestamp as created_at,
        current_timestamp as updated_at 
    from {{ source('ecommerce_oltp', 'error_response') }}
    where user_id is not null
    and product_id is not null
    and timestamp is not null
),
final as (
    select md5(user_id::text || product_id::text || timestamp::text || event_type::text || source::text) as event_sk,
    *
    from completed_orders
    union all

    select md5(user_id::text || product_id::text || timestamp::text || event_type::text || source::text) as event_sk,
    *
    from failed_orders

    union all
    select md5(user_id::text || product_id::text || timestamp::text || event_type::text || source::text) as event_sk,
    *
    from purchase

    union all
    select md5(user_id::text || product_id::text || timestamp::text || event_type::text || source::text) as event_sk,
    *
    from search_response

    union all
    select md5(user_id::text || product_id::text || timestamp::text || event_type::text || source::text) as event_sk,
    *
    from error_response
)

{% if is_incremental() %}
-- Incremental logic: Insert only new or updated rows
select * from final
where event_sk not in (select distinct event_sk from {{ this }})
{% else %}
-- Full refresh logic: Load all rows
select * from final
{% endif %}

