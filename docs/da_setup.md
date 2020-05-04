---
title: Installation
layout: docs
---

**In this section**

* TOC
{:toc}

----

## Prerequisites

To use the Tableau Data Acceleration client, you need the following:

* Python 3.5 or later (Check your version by typing `python --version`)
* Tableau Server version 2020.2 or later
* [Tableau Server Client (Python)](https://tableau.github.io/server-client-python/)
* Server or site administrator permissions

## Tableau Server Configuration

When using this feature, it is recommended to increase the size of the Tableau Server external cache to 2 GB or larger.

View your current Tableau Server external cache size setting:

* `tsm configuration get -k redis.max_memory_in_mb`

Set the Tableau Server external cache size to 2 GB:

* `tsm configuration set -k redis.max_memory_in_mb -v 2048`
* `tsm pending-changes apply`

## Running the Setup Script

Download the scripts from [https://github.com/tableau/tableau-data-acceleration-client/archive/master.zip](https://github.com/tableau/tableau-data-acceleration-client/archive/master.zip).

The `setup.py` script verifies and installs the dependencies of the `accelerate_workbooks.py` script. The script requires internet connectivity to download the libraries if they are not already installed.

To run the script on Windows type, `setup.py`. To run the script on Linux, type `sudo setup.py`.

These Python-based dependencies will be installed under `python\lib\site-packages`:

* python-dateutil 
* PTable 
* tableauserverclient 

## Troubleshooting Installation

### Error: No module named pip

An earlier version of Python that doesn't include the Python Package Installer (pip) might be installed on your server.

### Error: SSL CERTIFICATE_VERIFY_FAILED

The `setup.py` installation script requires internet connectivity to download the dependencies. You might see the errors, `Unable to download Tableau Server Client` or `SSL CERTIFICATE_VERIFY_FAILED`.

### To Install the Dependencies Manually

Optionally, you can manually install the dependencies without using `setup.py`. To do that, use the following commands:

* `python – m pip install python-dateutil` or `pip install python-dateutil`
* `python –m pip install PTABLE` or `pip install PTABLE`
* `python –m pip install tableauserverclient` or `pip install tableauserverclient`
