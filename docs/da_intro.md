---
title: Introduction
layout: docs
---

Tableau Server administrators can enable data acceleration for specific workbooks. An accelerated workbook loads faster because Tableau Server pre-computes the workbook's data in a background process.

Workbooks are not enabled for acceleration by default. The easiest way to configure data acceleration is to use the `accelerate_workbooks.py` Python script. It is also possible, but more difficult, to configure data acceleration using the Tableau Server REST API.

## Supported in This Release

To precompute the data, Tableau Server needs to connect to the data source in the background without requiring user interaction. Therefore, data acceleration is only supported for workbooks with embedded connection credentials.

Once enabled, data for workbooks with embedded extracts is automatically accelerated whereas workbooks with published and live data sources need to be added to an acceleration schedule.

## Not Supported in This Release

The following are currently not supported:

* Workbooks that use encrypted extracts
* Workbooks that prompt user for credentials
* Workbooks that use the Object Model framework.
* Workbooks that fetch data from federated data sources. Data blending is partially supported but data queried against secondary data sources is not accelerated

For more information about data acceleration and the resource implications of configuring it, see [Data Acceleration](https://help.tableau.com/v2020.2/server/en-us/data_acceleration.htm) in the Tableau Server documentation.
