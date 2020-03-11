---
title: Tutorial
layout: docs
---

**In this section**

* TOC
{:toc}

----

This tutorial shows you how to enable and schedule workbooks for data acceleration using the `accelerate_workbooks.py` command line tool.

Note: You must be signed in as a server administrator to create schedules or use site-level commands. For other commands, you can use the server administrator role or the site administrator role.

### Sign Into Tableau Server

`python accelerate_workbooks.py --server <server-url> --username <username> --password <password> --site <site>`

For information about how to identify the site value, see [Sign In and Out](https://tableau.github.io/server-client-python/docs/sign-in-out). If you don't specify a site, you will be signed into the Default site.  

### Enable Workbooks That Only Use Embedded Extracts

When data acceleration is enabled, a workbook that only has data sources that are embedded extracts does not require an acceleration schedule. Tableau Server automatically identifies the changes to its content and data whenever the workbook is republished or its extracts are refreshed (manually or on a schedule) and it submits a background task for the data pre-computation.  Thus, this type of workbook can be accelerated by just enabling it with the command:

`python accelerate_workbooks.py --enable "My Project/Embedded Extract Workbook"`

Note: If a workbook is in a nested project, its path may be like "Project 1/Project 2/Workbook Name". Workbook paths are case sensitive.

The server will enable the workbook and you will see the following output:

Workbooks enabled
Project/Workbook
My Project/Embedded Extract Workbook

After the background task for pre-computation of the workbook's data is completed, subsequent loads of the workbooks will use those pre-computed results. The background task may take a few minutes to finish.

### Schedule Workbooks With Published or Live Data Sources

Workbooks with published or live data sources need to be scheduled for acceleration, which keeps their data fresh.

This command will create an acceleration schedule called "My Schedule" that runs every 4 hours throughout the day.

`python accelerate_workbooks.py --create-schedule "My Schedule" --hourly-interval 4 --start-hour 0 --end-hour 23 --end-minute 45`

Next, we'll associate this acceleration schedule with your workbooks:

`python accelerate_workbooks.py --add-to-schedule "My Schedule" "My Project/My Workbook"`

You will see the following output:

Workbooks added to schedule
Project/Workbook             |  Schedules
My Project/My Workbook       |  My Schedule

Users can also attach multiple workbooks to "My Schedule" by using a path list.

`python accelerate_workbooks.py --add-to-schedule "My Schedule" --path-list pathfile.txt`

In the 'pathfile.txt' file, each line defines a workbook path.

My project/My Workbook
Finance Project/Expenses
Sales Project/Leads Per Region

Note: If a workbook uses only embedded extracts then an acceleration schedule will not be attached even when the user issues the `--add-to-schedule command`.

### Monitor Your Accelerated Workbooks

To see which workbooks have been enabled, use the `--status`, and `--show-schedules` commands.

Display all the workbooks that are enabled, and which acceleration schedules are associated.
`python accelerate_workbooks.py --status`

Display the accelerated schedules associated with workbooks.
`python accelerate_workbooks.py --show-schedules`

### Load Your Accelerated Workbooks and Check the Performance

#### Tableau Server Administrator Views  

Tableau Server provides an administrator view to review the load times for workbooks. See [Stats for Load Times](https://help.tableau.com/current/server/en-us/adminview_stats_load_time.htm).

### Sign Out of Tableau Server

Log out of Tableau Server and end your session.
`python accelerate_workbooks.py --logout`
