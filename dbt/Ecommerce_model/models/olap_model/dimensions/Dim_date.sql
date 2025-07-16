{{
    config(
        materialized='incremental',
        strategy='append',
        unique_key='date_sk',
        indexes=
        [
            {"columns":['date_sk'],'unique':true}
        ]
    )
}}
with dim_date as (
    select 
        distinct md5(timestamp || source) as date_sk,
        timestamp,
        extract(year from timestamp) as year,
        extract(month from timestamp) as month,
        extract(day from timestamp) as day,
        extract(week from timestamp) as week,
        extract(quarter from timestamp) as quarter
    from {{ ref('STG_Event') }}
)

{% if is_incremental() %}
select * from dim_date
where date_sk not in (select distinct date_sk from {{ this }})
{% else %}
select * from dim_date
{% endif %}