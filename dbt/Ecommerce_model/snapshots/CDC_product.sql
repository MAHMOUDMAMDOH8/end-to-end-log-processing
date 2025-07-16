{% snapshot CDC_product %}

{{
    config(
        target_schema='snapshots',
        unique_key='product_id',
        strategy='check',
        check_cols=['price', 'stock']
    )
}}

select 
    distinct product_id :: text as product_id,
    name :: text as product_name,
    category :: text as category,
    subcategory :: text as subcategory,
    brand :: text as brand,
    description :: text as description,
    price :: numeric as price,
    stock :: numeric as stock,
    rating :: numeric as rating,
    current_timestamp as snapshot_timestamp
from {{ source('ecommerce_oltp', 'products') }}
{% endsnapshot %}