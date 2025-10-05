select distinct c.region 
from marts.common.dim_center c 
where c.is_reporting_branch = true 
and REPORTING_BRAND_NAME != 'No Zone' 
and REPORTING_BRAND_NAME is not null 
and (c.closing_date < '2022-03-01' or c.closing_date is null)
order by c.region

