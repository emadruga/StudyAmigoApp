# AWS Aggregate Billing Reports — Two-Project Setup

## Overview

This document describes how to get daily AWS cost emails broken down by project (`study-amigo.app` and `metads.app`), with per-service line items, per-project subtotals, and a billing-cycle aggregate. Yes — **AWS Cost Allocation Tags** are the correct mechanism.

---

## 1. How It Works (Conceptual)

```
Resource Tags  ──►  AWS Cost Allocation Tags (activated in Billing)
                                │
                                ▼
                       Cost Explorer API
                                │
              ┌─────────────────┴─────────────────┐
              │                                   │
    Filter: Project=study-amigo         Filter: Project=metaads
              │                                   │
    Per-service costs                   Per-service costs
              │                                   │
              └──────────────┬────────────────────┘
                             │
                    Lambda (daily cron)
                             │
                    Formatted HTML email
                             │
                          SES / SNS
                             │
                        Your inbox
```

---

## 2. Current State of Tags

### `metads.app` — already tagged correctly
Every resource in `/Users/emadruga/proj/metaAds/aws_lambda_deploy/infra/` already applies:
```hcl
tags = {
  Project     = "metaads"
  Environment = var.environment   # "dev" or "prod"
  ManagedBy   = "terraform"
}
```

### `study-amigo.app` — needs tagging fix
Resources in `server/aws_terraform/main.tf` currently only have `Name` tags.
**Action required**: add `Project`, `Environment`, and `ManagedBy` tags to all resources.

---

## 3. Step-by-Step Plan

### Step 1 — Add `Project` Tags to Study-Amigo Terraform

Edit `server/aws_terraform/main.tf`. Add a `locals` block and a `default_tags` pattern (or tag each resource individually). The cleanest approach is to use provider-level `default_tags`, which automatically applies to every resource:

```hcl
# In variables.tf — add:
variable "environment" {
  type    = string
  default = "prod"
}

# In main.tf — update the provider block:
provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = var.project_name   # "study-amigo"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
```

With `default_tags`, you do **not** need to add tags to each individual resource block — Terraform merges them automatically. The existing `Name` tags on individual resources are preserved.

After the change:
```bash
cd server/aws_terraform
terraform plan   # verify only tag additions, no resource replacements
terraform apply
```

---

### Step 2 — Activate Cost Allocation Tags in AWS Billing Console

Cost tags must be explicitly activated before AWS tracks spending against them. This is a **one-time manual step per tag key**.

1. Go to **AWS Billing Console** → **Cost allocation tags**
   URL: `https://us-east-1.console.aws.amazon.com/billing/home#/tags`
2. Under **User-defined cost allocation tags**, find:
   - `Project`
   - `Environment`
   - `ManagedBy`
3. Select all three → click **Activate**
4. AWS notes that activation takes **up to 24 hours** to take effect and applies only to costs incurred **after** activation (not retroactively).

---

### Step 3 — Enable AWS Cost and Usage Reports (CUR) (Optional but Recommended)

CUR provides the most granular raw data. It is optional for the daily email approach (which uses the Cost Explorer API instead), but useful if you ever want to analyze data in Athena/QuickSight.

1. Go to **Billing** → **Cost & Usage Reports** → **Create report**
2. Configure:
   - Report name: `all-projects-daily`
   - Include resource IDs: **Yes**
   - Time granularity: **Daily**
   - Compression: Parquet or GZIP
   - S3 bucket: create a dedicated `billing-cur-ACCOUNTID` bucket
3. This delivers raw CSVs to S3 daily but does **not** send emails on its own.

---

### Step 4 — Build the Daily Email Report (Lambda + EventBridge + SES)

This is the core of the daily email system. A small Lambda queries the Cost Explorer API each morning and sends a formatted HTML email.

#### 4a. Architecture

```
EventBridge Scheduler (daily 08:00 UTC)
    └─► Lambda: billing-reporter
            ├─► Cost Explorer API (GetCostAndUsage)
            │       ├─ Filter: Tag[Project] = study-amigo
            │       └─ Filter: Tag[Project] = metaads
            └─► SES (SendEmail)  OR  SNS Topic (your email subscriber)
```

#### 4b. Lambda Implementation Sketch

```python
import boto3
from datetime import date, timedelta
import json

ce = boto3.client('ce', region_name='us-east-1')
ses = boto3.client('ses', region_name='us-east-1')

PROJECTS = ['study-amigo', 'metaads']
RECIPIENT = 'your@email.com'
SENDER    = 'billing@yourdomain.com'  # must be SES-verified

def get_costs_for_project(project: str, start: str, end: str) -> dict:
    """Returns service-level cost breakdown for a project tag."""
    resp = ce.get_cost_and_usage(
        TimePeriod={'Start': start, 'End': end},
        Granularity='DAILY',
        Filter={
            'Tags': {
                'Key': 'Project',
                'Values': [project],
                'MatchOptions': ['EQUALS']
            }
        },
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}],
        Metrics=['UnblendedCost']
    )
    return resp['ResultsByTime']

def get_billing_cycle_costs(project: str) -> dict:
    """Month-to-date costs for the current billing cycle."""
    today = date.today()
    start = today.replace(day=1).isoformat()
    end   = today.isoformat()
    resp = ce.get_cost_and_usage(
        TimePeriod={'Start': start, 'End': end},
        Granularity='MONTHLY',
        Filter={
            'Tags': {
                'Key': 'Project',
                'Values': [project],
                'MatchOptions': ['EQUALS']
            }
        },
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}],
        Metrics=['UnblendedCost']
    )
    return resp['ResultsByTime']

def build_html_report() -> str:
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    today     = date.today().isoformat()

    sections = []
    grand_daily_total = 0.0
    grand_mtd_total   = 0.0

    for project in PROJECTS:
        # Yesterday costs
        daily = get_costs_for_project(project, yesterday, today)
        services_daily = {}
        for period in daily:
            for group in period['Groups']:
                svc = group['Keys'][0]
                amt = float(group['Metrics']['UnblendedCost']['Amount'])
                services_daily[svc] = services_daily.get(svc, 0) + amt

        daily_total = sum(services_daily.values())
        grand_daily_total += daily_total

        # Month-to-date
        mtd = get_billing_cycle_costs(project)
        services_mtd = {}
        for period in mtd:
            for group in period['Groups']:
                svc = group['Keys'][0]
                amt = float(group['Metrics']['UnblendedCost']['Amount'])
                services_mtd[svc] = services_mtd.get(svc, 0) + amt

        mtd_total = sum(services_mtd.values())
        grand_mtd_total += mtd_total

        # Build section HTML
        rows_daily = ''.join(
            f'<tr><td>{s}</td><td>${v:.4f}</td></tr>'
            for s, v in sorted(services_daily.items(), key=lambda x: -x[1])
            if v > 0.0001
        )
        rows_mtd = ''.join(
            f'<tr><td>{s}</td><td>${v:.4f}</td></tr>'
            for s, v in sorted(services_mtd.items(), key=lambda x: -x[1])
            if v > 0.0001
        )

        sections.append(f"""
        <h2>{project}</h2>
        <h3>Yesterday ({yesterday}) — ${daily_total:.4f}</h3>
        <table border="1" cellpadding="4" style="border-collapse:collapse">
          <tr><th>Service</th><th>Cost (USD)</th></tr>
          {rows_daily or '<tr><td colspan=2>No charges</td></tr>'}
        </table>
        <h3>Month-to-date — ${mtd_total:.4f}</h3>
        <table border="1" cellpadding="4" style="border-collapse:collapse">
          <tr><th>Service</th><th>Cost (USD)</th></tr>
          {rows_mtd or '<tr><td colspan=2>No charges</td></tr>'}
        </table>
        <hr/>
        """)

    return f"""
    <html><body>
    <h1>AWS Daily Cost Report — {today}</h1>
    {''.join(sections)}
    <h2>Grand Total</h2>
    <table border="1" cellpadding="4" style="border-collapse:collapse">
      <tr><th>Period</th><th>Cost (USD)</th></tr>
      <tr><td>Yesterday</td><td>${grand_daily_total:.4f}</td></tr>
      <tr><td>Month-to-date</td><td>${grand_mtd_total:.4f}</td></tr>
    </table>
    </body></html>
    """

def handler(event, context):
    html = build_html_report()
    ses.send_email(
        Source=SENDER,
        Destination={'ToAddresses': [RECIPIENT]},
        Message={
            'Subject': {'Data': f'AWS Cost Report {date.today().isoformat()}'},
            'Body': {'Html': {'Data': html}}
        }
    )
    return {'statusCode': 200}
```

#### 4c. IAM Policy for the Lambda Role

The Lambda execution role needs:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ce:GetCostAndUsage",
        "ce:GetCostForecast"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ses:SendEmail",
        "ses:SendRawEmail"
      ],
      "Resource": "*"
    }
  ]
}
```

> **Note**: `ce:*` (Cost Explorer) calls are **global** — the Lambda must be in `us-east-1` to call the CE API, which is a global service always served from us-east-1.

#### 4d. EventBridge Scheduler Rule

```hcl
resource "aws_scheduler_schedule" "daily_billing_report" {
  name = "billing-reporter-daily"

  flexible_time_window { mode = "OFF" }

  schedule_expression          = "cron(0 8 * * ? *)"   # 08:00 UTC daily
  schedule_expression_timezone = "America/Sao_Paulo"    # adjust to your TZ

  target {
    arn      = aws_lambda_function.billing_reporter.arn
    role_arn = aws_iam_role.eventbridge_scheduler.arn
    input    = "{}"
  }
}
```

---

### Step 5 — Set Up AWS Budgets Per Project (Alert Layer)

Budgets are separate from daily reports — they send alerts when spend crosses a threshold. Both layers are complementary.

For each project, create a monthly budget with percentage-based alerts:

1. Go to **AWS Budgets** → **Create budget** → **Cost budget**
2. Scope it with tag filter:
   - Tag key: `Project`
   - Tag value: `study-amigo` (repeat for `metaads`)
3. Set a monthly budget amount (e.g., $10/month)
4. Add alert thresholds:
   - 50% actual → email
   - 80% actual → email
   - 100% actual → email
   - 100% forecasted → email (early warning)

You can also create a combined "all projects" budget with no tag filter to track total AWS spend.

---

### Step 6 — Verify Coverage with Cost Allocation Tag Report

After 24–48 hours of tags being active, verify that all spend is attributed:

1. **Cost Explorer** → **Reports** → **Cost by tag**
2. Group by `Project` tag
3. Look for a row labeled **No tag key** — this represents untagged spend
   If non-zero: some resource is missing the `Project` tag
   - Common culprits: data transfer, support charges, CloudFront usage fees, Route 53 hosted zones, S3 requests (these attach to the bucket's tag)

---

## 4. Terraform File to Add for the Billing Reporter

The billing Lambda can live in either project's infra or in a new shared `billing/` Terraform module. Recommended location since metaAds already has a well-structured infra:

```
/Users/emadruga/proj/metaAds/aws_lambda_deploy/infra/
├── billing.tf          ← new file: Lambda + EventBridge + IAM role
└── lambda_src/
    └── billing_reporter/
        └── handler.py  ← the Lambda code above
```

Or as a standalone directory:
```
~/proj/aws_billing_reporter/
├── main.tf
├── lambda.tf
├── iam.tf
├── src/
│   └── handler.py
```

---

## 5. SES Setup (One-Time)

Cost Explorer calls work immediately, but SES requires verification:

1. Go to **SES Console** → **Verified identities** → **Create identity**
2. Verify either:
   - Your **email address** (easiest for personal use — just click the verification link)
   - Your **domain** (recommended for `@study-amigo.app` or `@metads.app`)
3. If your AWS account is in the **SES sandbox**, you can only send to verified email addresses. To send to any address: request **production access** (takes 1–2 days, just fill the form).

---

## 6. Summary Checklist

| # | Task | Where | Status |
|---|------|--------|--------|
| 1 | Add `provider default_tags` to study-amigo Terraform | `server/aws_terraform/main.tf` | TODO |
| 2 | `terraform apply` study-amigo infra to push new tags | local → AWS | TODO |
| 3 | Activate `Project`, `Environment`, `ManagedBy` cost allocation tags | AWS Billing Console | TODO |
| 4 | Verify SES sender email/domain | AWS SES Console | TODO |
| 5 | Deploy billing reporter Lambda | new Terraform module | TODO |
| 6 | Create EventBridge rule for daily 08:00 UTC | same Terraform module | TODO |
| 7 | Create per-project Budgets with % alerts | AWS Budgets Console | TODO |
| 8 | Wait 24–48 h, check Cost Explorer tag coverage | Cost Explorer Console | TODO |

---

## 7. Cost of the Billing System Itself

| Component | Cost |
|-----------|------|
| Lambda invocations (1/day) | ~$0.00 |
| Cost Explorer API calls (~4 calls/day) | $0.01 per 1000 requests → ~$0.12/year |
| SES email (1/day) | $0.10 per 1000 emails → ~$0.04/year |
| EventBridge Scheduler | $1.00 per million invocations → ~$0.00/year |
| **Total** | **< $0.20/year** |
