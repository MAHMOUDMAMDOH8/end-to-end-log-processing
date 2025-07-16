{{
    config(
        materialized='incremental',
        strategy='append',
        unique_key='order_sk',
        target_schema='gold',
        indexes=[
            {"columns":['order_sk'],'unique':true}
        ]
    )
}}

with fact_order as(
    select
        O.order_sk,
        U.user_sk,
        P.product_sk,
        D.date_sk,
        O.quantity::int,
        O.amount::numeric,
        O.payment_method,
        O.status
    from {{ ref('STG_orders') }} O left join {{ ref('Dim_date') }} D on O.timestamp = D.timestamp
    left join {{ ref('Dim_product') }} P on O.product_id = P.product_id
    left join {{ ref('Dim_users') }} U on O.user_id = U.user_id
)

{% if is_incremental() %}
select * from fact_order
where order_sk not in (select distinct order_sk from {{ this }})
{% else %}
select * from fact_order
{% endif %}