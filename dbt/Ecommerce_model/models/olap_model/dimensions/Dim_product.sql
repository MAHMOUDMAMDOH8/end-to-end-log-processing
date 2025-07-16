{{
    config(
        materialized='incremental',
        strategy='append',
        unique_key='product_sk',
        indexes=
        [
            {"columns":['product_sk'],'unique':true}
        ]
    )
}}

with products as (
    select 
        *
    from {{ ref('STG_Products') }}
)

{% if is_incremental() %}
select * from products
where product_sk not in (select distinct product_sk from {{ this }})
{% else %}
select * from products
{% endif %}
