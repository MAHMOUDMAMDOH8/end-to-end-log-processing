{{
    config(
        materialized='incremental',
        unique_key='product_sk',
        indexes=[{"columns": ['product_sk'], "unique": true}],
        target_schema='staging'
    )
}}

with valid_products as (
    select 
        product_id,
        product_name,
        category,
        subcategory,
        brand,
        description,
        price,
        stock,
        rating,
        'supabase' as source,
        current_timestamp as created_at,
        current_timestamp as updated_at
    from {{ ref('CDC_product') }} 
),
final as (
    select 
        md5(product_id || source) as product_sk, *
    from valid_products
)

{% if is_incremental() %}
-- Incremental logic: Insert only new or updated rows
select * from final
where product_sk not in (select distinct product_sk from {{ this }})
{% else %}
-- Full refresh logic: Load all rows
select * from final
{% endif %}

