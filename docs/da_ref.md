---
title: Command Reference
layout: docs
---

**In this section**

* TOC
{:toc}

----

Note: Optional arguments are indicated with [].

### Get Help

Get a list of the available commands.

`python accelerate_workbooks.py --help`

### Sign Into Tableau Server

In Tableau Server, creating schedules and site level commands require the user to be signed in with an account with the Server Administrator role.  For other commands the Server Administrator role or the Site Administrator role is required.

`python accelerate_workbooks.py [--server] [SERVER_URL] [--site] [SITE_NAME] [--username] [Username] [--password] [password]`

SITE_NAME is the sub-path of your full site URL (also called contentURL in the REST API).  Given the site URL 'https://my.tableauserver.com/MYSITE', 'MYSITE' is the site name.  See [Sign In and Out](https://tableau.github.io/server-client-python/docs/sign-in-out) for identifying the [SITE_NAME]. When `--site` is not specified or is specified with "" the Default site will be used.

After a successful sign in, a session token file (".token_profile") will be created and saved in the same directory as `accelerate_workbooks.py`. The token file will be deleted when you log out.  

Example: Sign into Tableau Server and the Default site

`python accelerate_workbooks.py --server https://server --site "" --username user1 --password password1`

You can ignore the SSL Certificate by pressing the ENTER key when prompted.

Example: Sign into Tableau Server with an SSL certificate

`python accelerate_workbooks.py --server https://server --site "" --username user1 --password password1 --ssl-cert-pem cert.pem`

Example: Switch the site that you are logged into

`python accelerate_workbooks.py --server https://server --username user1 --password password1 --site different_site`

Example: For some usernames and passwords it may be necessary to use double quotes.

`python accelerate_workbooks.py --server https://server --site "" --username "user space name" --password "password with spaces"`

Example:  Double quotes "" should not be used when prompted for input:

`python accelerate_workbooks.py --server https://server`

site (hit enter for the Default site):
username: user space name
password: password with spaces
path to ssl certificate (hit enter to ignore): cert.pem

### Sign Out of Tableau Server

The session token file (".token_profile") created on login will be deleted when you log out.

Example:  Sign out of Tableau Server

`python accelerate_workbooks.py --logout`

When successfully signed out of Tableau Server, you will see the following message, "Signed out from current connection to https://server successfully". If you are not connected to an existing server, you will see the following message, "No existing connection to any server."

### Create Data Acceleration Schedules

The following command is used to create a data acceleration schedule.

`python accelerate_workbooks.py --create-schedule SCHEDULE_NAME INTERVAL_TYPE [INTERVAL] [START_TIME] [END_TIME]`

In Tableau Server, creating schedules requires the Server Administrator role. For other commands the Server Administrator role or the Site Administrator role is sufficient.

INTERVAL_TYPE can be one of the four options below:
--hourly-interval with INTERVAL in {0.25,0.5,1,2,4,6,8,12}, the unit is hour.
--daily-interval, INTERVAL is not needed
--weekly-interval with INTERVAL as a non-empty subset of:
{Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday}
--monthly-interval, INTERVAL is the starting day in a month.

[START_TIME] is optional. If no starting time is specified, the default time 00:00:00 is used. To specify the starting time, `--start-hour` and `--start-minute` can be used to specify the time. For example, let's look at the following command:

`python accelerate_workbooks.py --create-schedule --hourly-interval 0.25 --start-hour 18 --start-minute 30`

In this example, the schedule is for every 15 minutes, starting at 18:30 (6:30 PM) every day. The next schedule is 18:45, 19:30, 19:45, and so on until the day restarts at midnight or until the specified `--end-hour` and `--end-minute` are reached. It will not run at 19:00, 19:15, 20:00, and so on because `--start-minute` is set to 30 which means that it's only scheduled to start on minute 30 of each hour. It will not run on 1:30, 6:30, 17:30, and so on because `--start-hour` is set to 18 which means it's only scheduled to start on hour 18 of each day.

[END_TIME] is optional. If no end time is specified, the end of the day will be used. To specify the ending time, `--end-hour` and `--end-minute` can be used to specify the time. END_TIME option is only useful for hourly interval.

The warning, "Warning: The recurrence interval of the given schedule is larger than Vizql server data refresh interval of 720 minutes." will be displayed if the users try to create a schedule that exceeds the configured VizQL server data refresh interval. By default, this is set to 12 hours (720 minutes).

Example 1: Create a scheduled pre-computation every 4 hours.
  
In this example, a pre-computation background task will be submitted every 4 hours throughout the day.

`python  accelerate_workbooks.py --create-schedule "My Schedule"  --hourly-interval 4 --start-hour 0 --end-hour 23 --end-minute 45`

After the acceleration schedule is created using the command line client, it can be viewed in the Tableau Server Schedules view. The scheduled task type will not currently be displayed.  

### Associate Workbooks to a Schedule

You can associate a workbook to single or multiple data acceleration schedules. If your workbook has not been enabled for acceleration, the `--add-schedule` command will automatically enable the workbook.  

`python accelerate_workbooks.py --add-to-schedule [SCHEDULE_NAME] --workbook-path WORKBOOK_PATH`

`python accelerate_workbooks.py --add-to-schedule [SCHEDULE_NAME] --path-list PATH_LIST`

Example 1: Associate a workbook to a schedule

`python accelerate_workbooks.py --add-to-schedule "My Schedule" --workbook-path project/workbook1`

```iecst
Workbooks added to schedule
Project/Workbook     | Schedules
Default/my workbook1 | My Schedule
```

Example 2:  Associate an acceleration schedule using a text file with a path list containing one or more workbooks.

`python accelerate_workbooks.py --add-to-schedule "My Schedule" --path-list path.txt`

```iecst
Workbooks added to schedule
Project/Workbook    Schedules
Default/my workbook1    My Schedule
Default/my workbook2    My Schedule
```

Example 3:  Associate acceleration schedules with a workbook that is only extract data source based.

Any workbook that uses only embedded extracts as its data source does not require an explicit acceleration schedule and thus it will only be enabled for acceleration without using an acceleration schedule.  For these workbooks, the Tableau Server will automatically identify changes to the workbook content and data.  Whenever the workbook is republished or its extract refreshes (manually or scheduled) a background task is submitted to pre-compute the data.  

In the example below, an attempt was made to add "My Schedule" to a workbook with only embedded extracts. The workbook is enabled for acceleration and it is not added to the "My Schedule" acceleration schedule.

`python accelerate_workbooks.py --add-to-schedule "My schedule" Default/WorkbookwithOnlyExtracts`

```iecst
Workbooks added to schedule: None
Warning: Unable to add workbook "Default/WorkbookwithOnlyExtracts" to schedule due to Workbook with id 10000 uses only embedded extract(s) and does not need explicit scheduling for acceleration. It was enabled for acceleration but not attached to the given schedule.
```

`python accelerate_workbooks.py --show-schedule`

```iecst
Workbooks added to schedule
Project/Workbook    Schedules
Default/my workbook1    My Schedule
Default/my workbook2    My Schedule
```

For workbooks that are not supported you will see the following warnings:

Workbooks with encrypted embedded extracts:
`Unable to enable Default/Sales. Workbook 'Sales' is not supported for data acceleration because it only uses encrypted embedded extracts as data sources.`

Workbooks where credentials are not embedded:
`Unable to enable Default/Finance. Workbook 'Finance' is not supported for data acceleration because it uses data sources without embedding credentials.`

The following warning will be displayed if the users try to create a schedule that exceeds the configured VizQL server data refresh interval.  By default, this is set to 12 hours (720 minutes).
`Warning: The recurrence interval of the given schedule is larger than Vizql server data refresh interval of 720 minutes.`

### Enable Workbooks

Enabling a workbook will opt in the workbook for acceleration. data acceleration will monitor the relevant Tableau events that could potentially change the data of the workbooks such as workbook publishing, extract refreshing (if the workbook has any) and web authoring.  Pre-computation will be triggered after these events. However, the data source changes which are not managed by Tableau will not be monitored and the acceleration schedule is used for keeping the pre-computed data up to date in those scenarios.  

To enable one workbook:

`python accelerate_workbooks.py --enable [--workbook-path] WORKBOOK_PATH`

To enable one or more workbooks in batches, you can provide a file specifying a list of workbooks.

`python accelerate_workbooks.py --enable [--path-list] PATH_LIST`

Example 1:  Enable a single workbook

`python accelerate_workbooks.py --enable Default/Workbook1`

Example 2:  Enable multiple workbooks

Create a path file for example `paths.txt` using the format below project/workbook:
Default/Workbook1
Default/Workbook2
The following command will enable the workbooks defined in the paths.txt file.

`python accelerate_workbooks.py --enable --path-list paths.txt`

```iecst
Workbooks enabled
Project/Workbook
Default/my workbook1
Default/my workbook2
```

For workbooks that are not currently supported, you will see the following warnings:

Workbooks with encrypted embedded extracts:
`Unable to enable Default/Sales. Workbook 'Sales' is not supported for data acceleration because it only uses encrypted embedded extracts as data sources.`

Workbooks where credentials are not embedded:
`Unable to enable Default/Finance. Workbook 'Finance' is not supported for data acceleration because it uses data sources without embedding credentials.`

### Detach a Workbook from a Schedule

Use the `--remove-from-schedule` command to detach a workbook from a schedule.

`python accelerate_workbooks.py --remove-from-schedule SCHEDULE_NAME [--workbook-path] WORKBOOK_PATH`

`python accelerate_workbooks.py --remove-from-schedule SCHEDULE_NAME [--path-list] PATH_LIST`

`python accelerate_workbooks.py --remove-from-schedule SCHEDULE_NAME project/workbook`

Example 1:  Removing multiple workbooks from a schedule using --path-list.  
In the example below "workbook1" and "workbook2" was detached from the acceleration schedule "My Schedule".  Any workbooks included in the path list are not associated with "My Schedule".

`python accelerate_workbooks.py --remove-from-schedule "My Schedule" --path-list "paths.txt"`

```iecst
Workbooks removed from schedule
Project/Workbook    Schedules
Default/workbook1    My Schedule
Default/workbook2    My Schedule

Workbooks not on schedule "My Schedule"
Project/Workbook
Default/extractworkbook
```

Example 2:  Remove a workbook from a schedule

`python accelerate_workbooks.py --remove-from-schedule "My Schedule" Default/workbook1`

```iecst
Workbooks removed to schedule
Project/Workbook    Removed From Schedule
Default/my workbook1    My Schedule
```

Example 3:

`python accelerate_workbooks.py --remove-from-schedule "My Schedule" --workbook-path Default/workbook1`

```iecst
Workbooks removed from schedule
Project/Workbook    Schedules
Default/workbook1    My Schedule
```

### Delete a Schedule

Use the `--delete-schedule` command to delete a schedule. This deletes the schedule whether it is referenced by a workbook or not. If a workbook is associated with the schedule, the workbook remains enabled but the schedule is deleted.

`python accelerate_workbooks.py --delete-schedule SCHEDULE_NAME`

### Accelerate On-Demand

You can use `--enable` combined with `--accelerate-now` to submit a backgrounder pre-computation job on demand.  This can be useful to trigger a pre-computation ahead of the next scheduled run.

`python accelerate_workbooks.py --enable --accelerate-now --path-list PATH_LIST`

`python accelerate_workbooks.py --enable WORKBOOK_PATH --accelerate-now`

Example 1:

`python accelerate_workbooks.py --enable Default/workbook1 --accelerate-now`

### Disable Workbooks

Disabling a workbook stops accelerating the workbook. It detaches the workbook from the workbook's associated schedules and cleans up all of the acceleration artifacts related to the workbook. It will not remove entries from the Tableau query cache.

`python accelerate_workbooks.py --disable [--workbook-path] WORKBOOK_PATH`

`python accelerate_workbooks.py --disable --path-list PATH_LIST`

`python accelerate_workbooks.py --disable --workbook-path Default/workbook1`

```iecst
Workbooks Disabled
Project/Workbook
Default/workbook1
```

### Enable or Disable a Site for Data Acceleration

The following commands are used to enable or disable a site for acceleration.

`python accelerate_workbooks.py --enable --site SITE_NAME --type site`

`python accelerate_workbooks.py --disable --site SITE_NAME --type site`

Workbooks can only be enabled for acceleration if their site is enabled. Enabling a site will not enable any workbooks automatically. All sites are enabled for acceleration by default. Enabling a site is only needed when a site is explicitly disabled, or a site is imported from another Tableau Server.

Disabling a site for acceleration will disable all workbooks that were currently enabled for acceleration.  Once a site is disabled, no workbooks can be enabled on this site until this site is enabled again. All workbooks under that site will be disabled and detached from any accelerated schedules they are associated with.

In Tableau Server, to enable or disable acceleration requires the user to be signed in with an account with the Server Administrator role.

Example 1:  Disable the Default site for acceleration

`python accelerate_workbooks.py --disable --site SITE_NAME --type site`

Example 2:  Enable the Default site for acceleration

`python accelerate_workbooks.py --enable --site SITE_NAME --type site`

### Show Acceleration Status

The `--status` command shows the list of workbooks enabled for acceleration and the scheduled tasks for data acceleration.  When a workbook is enabled but not associated with any schedule, an asterisk '*' will be shown in the Schedule column. In that case, the pre-computed data for workbooks will be updated when the workbooks are re-published, or their extracts (if they have any) get refreshed.  Workbooks that only contain embedded extracts will not be associated with schedules.

`python accelerate_workbooks.py --status`

Example 1: Display the status of all enabled and scheduled accelerated workbooks.

`python accelerate_workbooks.py --status`

```iecst
Data Acceleration is enabled for the following workbooks
Site    Project/Workbook
Default    Default/extractworkbook
Default    Default/liveworkbook
Default    Default/liveandextractworkbook

Scheduled Tasks for Data Acceleration
Project/Workbook                 Schedule      Next Run
Default/extractworkbook          *    
Default/liveworkbook             My Schedule   2020-01-22 16:00:00-08:00
Default/liveandextractworkbook   My Schedule   2020-01-22 16:00:00-08:00

*The Data Acceleration views for these workbooks will be updated when they are published, or when their extract is refreshed.
```

### Show Acceleration Schedules

The `--show-schedules` command displays the schedule information for enabled workbooks associated with their accelerated schedules. The schedule information includes the schedule name associated with the workbooks and their next run time.

`python accelerate_workbooks.py --show-schedules`

`python accelerate_workbooks.py --show-schedules SCHEDULE_NAME [--workbook-path] [WORKBOOK_PATH]`

`python accelerate_workbooks.py --show-schedules SCHEDULE_NAME [--path-list] [PATH_LIST]`

Note: If `--workbook-path` or `-–path-list` are omitted, the command will show all the enabled workbooks with their schedule information.

Example 1:  When there are no data acceleration schedules associated with enabled workbooks

`python accelerate_workbooks.py --show-schedules`

Scheduled Tasks for Data Acceleration: None

Example 2:  When there are enabled workbooks with data acceleration schedules

```iecst
Scheduled Tasks for Data Acceleration
Project/Workbook                 Schedule       Next Run
Default/extractworkbook          *    
Default/liveworkbook             My Schedule    2020-01-22 16:00:00-08:00
Default/liveandextractworkbook   My Schedule    2020-01-22 16:00:00-08:00
```

### Show Acceleration Tasks

The `--show-tasks` command displays the scheduled tasks for data acceleration. The information includes the project and workbook name, the schedule name associated with the workbooks, and their next run time.

`python accelerate_workbooks.py --show-tasks`

```iecst
Scheduled Tasks for Data Acceleration
Project/Workbook               Schedule      Next Run At
Default/myworkbook             My Schedule   2020-01-22 16:00:00-08:00
```

### Show Acceleration Benefit Summary

The `--compare` command displays a summary of the acceleration benefit for enabled workbooks.

`python accelerate_workbooks.py --compare`

### Specify workbook paths

This section describes how to specify the workbook path argument and the path list argument in the commands `--add-to-schedule`, `--enable`, `--remove-from-schedule`.

--workbook-path
[WORKBOOK_PATH] is the path concatenating the project path and the workbook name by "/" where the project path is the path of the project directly containing the workbook to the root project.  The path is in the form of "Project Name/Workbook Name". If a workbook is in a nested project, its path may be like "Project 1/Project 2/Workbook Name". Workbook paths are case sensitive.

Double quotes are required for specifying the workbook path if it contains whitespace.

`python accelerate_workbooks.py --enable [--workbook-path] PATH_LIST`

Example 1: Specifying --workbook-path

`python accelerate_workbooks.py --enable --workbook-path "project/workbook with spaces"`

Example 2:  --workbook-path is optional

`python accelerate_workbooks.py --enable project/workbook`

Example 3:  --workbook-path is optional

`python accelerate_workbooks.py --add-to-schedule "My Schedule" project/workbook`

--path-list
PATH_LIST is a text file where each line is a workbook path. In the PATH_LIST, there is no need to use double quotes for workbook paths that contain whitespace.

Here is an example paths text file:
projectLevel1/projectLevel2/workbook1
project1/workbook2

Example 1:  Enable multiple workbooks

`python accelerate_workbooks.py --enable --path-list paths.txt`

Example 2:  Add multiple workbooks to a schedule.

`python accelerate_workbooks.py --add-to-schedule "My Schedule" --path-list paths.txt`

Example 3:  Remove multiple workbooks from a schedule.

`python accelerate_workbooks.py –-remove-from-schedule "My Schedule" --path-list paths.txt`
