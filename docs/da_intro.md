---
title: Introduction
layout: docs
---

Tableau Server administrators can enable data acceleration for specific workbooks. An accelerated workbook loads faster because Tableau Server pre-computes the workbook's data in a background process.

Workbooks are not enabled for acceleration by default. The easiest way to configure data acceleration is to use the `accelerate_workbooks.py` Python script. It is also possible, but more difficult, to configure data acceleration using the Tableau Server REST API.

For more information about data acceleration, what is supported and not supported, and the resource implications of configuring it, see [Data Acceleration](https://help.tableau.com/current/server/en-us/data_acceleration.htm) in the Tableau Server documentation.
