-- Show acceleration status for sheets
-- Assuming all workbooks are in site Default and project Default
select public.workbooks.name as WORKBOOK_NAME, 
       public.views.name as VIEW_NAME, 
       case 
        when public.materialized_views_sheet_status.state = 0 then 'Disabled'
        when public.materialized_views_sheet_status.state = 1 then 'Enabled' 
        when public.materialized_views_sheet_status.state = 2 then 'Materialization Job Submitted'
        when public.materialized_views_sheet_status.state = 5 then 'Materialization Job Failed'
        when public.materialized_views_sheet_status.state in (6,7,9) then 'Materialization Job Completed'
      end as WORKBOOK_ACCELERATION_JOB_STATUS,
      change_timestamp
from public.materialized_views_sheet_status 
inner join public.workbooks on public.materialized_views_sheet_status.workbook_id = public.workbooks.id
inner join public.views on public.materialized_views_sheet_status.view_id = public.views.id
