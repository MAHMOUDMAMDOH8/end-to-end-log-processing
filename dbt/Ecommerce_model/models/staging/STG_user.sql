{{ 
    config(
        materialized='incremental',
        strategy='append',
        unique_key='user_sk',
        indexes=[{"columns": ['user_sk'], "unique": true}],
        target_schema='staging'
    )
}}

with valid_users as (
    select 
        distinct user_id :: text as user_id,
        username :: text as username,
        username :: text as email,
        full_name :: text as full_name,
        sex :: text as sex,
        age :: numeric as age,
        country :: text as country,
        city :: text as city,
        'supabase' as source,
        current_timestamp as created_at,
        current_timestamp as updated_at
    from {{ source('ecommerce_oltp', 'users') }}

),
final as (
    select
        md5(user_id || source) as user_sk, *
    from valid_users
)

{% if is_incremental() %}
select * from final
where user_sk not in (select distinct user_sk from {{ this }})
{% else %}
select * from final
{% endif %}