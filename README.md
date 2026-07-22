# Enterprise Security Audit Aggregator

> Automated Windows and Linux Security Compliance Assessment Framework

## Overview

Enterprise Security Audit Aggregator is a modular Python framework that
automates security compliance verification for Windows and Linux
servers.

It processes customer ZIP packages, automatically detects the operating
system, evaluates configurable security requirements, and generates
consolidated Excel reports.

## Features

-   Windows Server assessment
-   Linux (Ubuntu) assessment
-   Automatic OS detection
-   Customer ZIP processing
-   Multi-server assessment
-   JSON-driven requirements
-   Modular parser architecture
-   Detailed Excel reporting

## Supported Requirements

  Requirement                         Windows   Linux
  ---------------------------------- --------- -------
  3.1 Audit Log Retention               ✅       ✅
  4.1 Password Policy                   ✅       ✅
  4.2 Forbidden Password                 △        △
  7 Privileged Account Audit            ✅       ✅
  9.1 Account Management Audit          ✅       ✅
  9.2 Authentication Log Retention      ✅       ✅

## Architecture

``` text
Customer ZIP
      │
      ▼
 ZIP Extraction
      │
      ▼
 Server Discovery
      │
      ▼
 Operating System Detection
      │
 ┌────┴────┐
 ▼         ▼
Windows   Linux
 │          │
 ▼          ▼
Parsers
      │
      ▼
Compliance Engine
      │
      ▼
Excel Report
```

## Project Structure

``` text
SecurityAuditAggregator/
├── analyzers/
├── parsers/
├── reports/
├── config/
│   ├── workflows/
│   ├── requirements/
│   └── mappings/
├── zip_processor/
├── models/
├── tests/
├── input/
├── output/
└── README.md
```

## Installation

``` bash
git clone https://github.com/<your-username>/SecurityAuditAggregator.git
cd SecurityAuditAggregator
python -m venv .venv
```

Windows:

``` bash
.venv\Scripts\activate
```

Linux:

``` bash
source .venv/bin/activate
```

``` bash
pip install -r requirements.txt
```

## Usage

Linux test:

``` bash
python -m tests.test_linux_server_engine
```

Customer assessment:

``` bash
python -m tests.test_customer_report
```

Input:

``` text
input/
└── CustomerResults.zip
```

Output:

``` text
output/
└── Customer_Security_Report_YYYYMMDD_HHMMSS.xlsx
```

## Report

### 設定状況

Compliance summary.

### 詳細結果

-   Hostname
-   Operating System
-   IP Address
-   Requirement
-   Expected Value
-   Actual Value
-   Result

Symbols:

  Symbol   Meaning
  -------- -----------------
  ○        PASS
  ×        FAIL
  △        Manual
  －       Not Implemented

## Roadmap

Completed: - Windows support - Linux support - Excel reporting -
Multi-server processing - OS detection

Planned: - Streamlit UI - HTML dashboard - PDF reports - AI
remediation - Azure integration - SharePoint integration - Docker - REST
API

## Author

**Lansana Baldé**

Cloud & Security Engineer
