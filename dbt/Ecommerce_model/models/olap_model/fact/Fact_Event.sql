{{
    config(
        materialized='incremental',
        strategy='append',
        unique_key='event_sk',
        target_schema='gold',
        indexes=[
            {"columns":['event_sk'],'unique':true}
        ]
    )
}}

with fact_event as(
    select
        E.event_sk,
        U.user_sk,
        P.product_sk,
        D.date_sk,
        event_type,
        session_id,
        device_type,
        geo_country,
        geo_city
    from {{ ref('STG_Event') }} E left join {{ ref('Dim_date') }} D on E.timestamp = D.timestamp
    left join {{ ref('Dim_product') }} P on E.product_id = P.product_id
    left join {{ ref('Dim_users') }} U on E.user_id = U.user_id
)

{% if is_incremental() %}
select * from fact_event
where event_sk not in (select distinct event_sk from {{ this }})
{% else %}
select * from fact_event
{% endif %}
