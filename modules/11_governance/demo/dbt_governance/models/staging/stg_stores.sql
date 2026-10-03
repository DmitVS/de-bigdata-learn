select store_id, city_id, status = 'open' as is_open from {{ source("retail_oltp", "stores") }}
