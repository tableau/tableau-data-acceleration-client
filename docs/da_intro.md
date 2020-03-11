---
title: Introduction
layout: docs
---

Tableau Server administrators can enable data acceleration for specific workbooks. An accelerated workbook loads faster because Tableau Server pre-computes the workbook's data in a background process.

The easiest way to configure data acceleration is to use the `accelerate_workbooks.py` Python script. It is also possible, but more difficult, to configure data acceleration using the Tableau Server REST API.

Workbooks with published and live data sources (both with embedded credentials), and workbooks with embedded extracts are supported. Workbooks with embedded extracts do not need to be scheduled. Workbooks with published and live data sources need to have a data acceleration task added to a schedule.

Not supported, are workbooks with encrypted extracts or workbooks that include user-based, now(), today() functions. Federated data sources are not supported. Data Blending is partially supported for acceleration; Data queried against the secondary data sources is not accelerated.

## Limitations

* Site and Server Administrator permission are required to control data acceleration.
* Only those workbooks with embedded credentials can be accelerated.
* The pre-computed data is saved into the Tableau Cache.  The cache is subject to the cache size limit and the cache expiration limit. We recommend that you review your configuration and recommend 2GB or larger.
* When you attach an acceleration schedule to a workbook, if that acceleration schedule interval exceeds the Tableau Server cache expiration time, the workbook will not be accelerated during the period between the cache expiration time and the next run of the acceleration schedule.  The workbook will revert to using the databases. By default, the Tableau Server cache expiration time is 12 hours (720 minutes).
* Workbooks using encrypted extracts or that include user-based, now(), today() functions are not supported currently and will not be accelerated.
* Federated Data Source is not supported for acceleration. When there is a workbook containing both federated data sources and other data sources, the data queried against federated data sources will not be accelerated.
* Data Blending is partially supported for acceleration. Data queried against the secondary data sources are not accelerated.
* Data acceleration schedules are not currently supported to be created in the Tableau Server schedules view.  

## Prerequisites

To use this tool, you need the following:

* Tableau Server version 2020.2 or later
* [Tableau Server Client (Python)](https://tableau.github.io/server-client-python/)
* Server or site administrator permissions

When using this feature, it is recommended to increase the size of the Tableau Server external cache to 2 GB or larger.

View your current Tableau Server external cache size setting:
`tsm configuration get -k redis.max_memory_in_mb`

Set the Tableau Server external cache size to 2 GB:
`tsm configuration set -k redis.max_memory_in_mb -v 2048`
`tsm pending-changes apply`
