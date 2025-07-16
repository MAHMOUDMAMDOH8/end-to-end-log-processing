{{
    config(
        materialized='incremental',
        strategy='append',
        unique_key='user_sk',
        indexes=[
            {"columns":['user_sk'],'unique':true}
        ]
    )
}}

with users as (
    select 
        distinct user_sk,
        user_id,
        username,
        email,
        sex,
        age,
        country,
        city,
        source
    from {{ ref('STG_user') }}
)

{% if is_incremental() %}
select * from users
where user_sk not in (select distinct user_sk from {{ this }})
{% else %}
select * from users
{% endif %}