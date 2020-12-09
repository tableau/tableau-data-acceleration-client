-- Disables a sheet for data acceleration
-- Assuming all workbooks are in site Default and project Default
with names as (
  select 'put your workbook name here' as workbook_name,
         'put your sheet name here' as sheet_name
)

update public.materialized_views_sheet_status status set state = 0
where status.view_id in (
	select id from views where name = (select sheet_name from names)
) and status.workbook_id = (
	select id from workbooks where name = (select workbook_name from names)
)