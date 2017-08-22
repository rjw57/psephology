# Test data for Psephology

This directory holds some testing data for the Psephology application.

## Requirements

Some scripts in this directory require Python packages beyond those required for
``psephology``. Install via:

```console
$ pip install -r data-requirements.txt
```

## HoC-GE2017-constituency-results.csv

This file forms part of a [UK Parliament
Report](http://researchbriefings.parliament.uk/ResearchBriefing/Summary/CBP-7979)
on the General Election 2017 and consists of Constituency summaries.

The script ``to_results.py`` can be used to parse this file. The results file,
``ge2017_results.txt``, was generated with this script.
