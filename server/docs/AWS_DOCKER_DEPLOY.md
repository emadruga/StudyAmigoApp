# AWS Docker Deployment Guide for StudyAmigo

This guide provides a complete step-by-step procedure for deploying the StudyAmigo flashcard application on AWS EC2 using Docker, with Cloudflare handling DNS and SSL termination.

**Architecture:**

```
User Browser
    │ (HTTPS)
    ▼
Cloudflare Proxy (study-amigo.app)
    │ (HTTP, proxied)
    ▼
AWS EC2 (t4g.micro, Elastic IP)
    │
    ├── Docker: flashcard_client (Nginx on port 80)
    │       ├── Serves React static files
    │       └── Reverse proxies API calls ──► Docker: flashcard_server (Gunicorn on port 8000)
    │
    └── EBS Volume: SQLite databases (admin.db, user_dbs/)
```

**Estimated Monthly Cost:** ~$6-9/month (with 1-year Reserved Instance discount applied manually).

---

## Table of Contents

1.  [Prerequisites](#1-prerequisites)
2.  [AWS Account Setup & CLI Credentials](#2-aws-account-setup--cli-credentials)
3.  [Install Terraform](#3-install-terraform)
4.  [Generate an SSH Key Pair](#4-generate-an-ssh-key-pair)
5.  [Configure Terraform Variables](#5-configure-terraform-variables)
6.  [Deploy Infrastructure with Terraform](#6-deploy-infrastructure-with-terraform)
7.  [Configure Cloudflare DNS](#7-configure-cloudflare-dns)
8.  [Configure Cloudflare SSL Settings](#8-configure-cloudflare-ssl-settings)
9.  [Verify the Deployment](#9-verify-the-deployment)
10. [Purchase a Reserved Instance (Cost Optimization)](#10-purchase-a-reserved-instance-cost-optimization)
11. [Ongoing Operations](#11-ongoing-operations)
12. [Terraform Script Structure](#12-terraform-script-structure)
13. [Tear Down](#13-tear-down)

---

## 1. Prerequisites

Before starting, ensure you have the following installed on your **local machine**:

-   **AWS CLI v2**: For authenticating Terraform with your AWS account.
-   **Terraform**: Infrastructure-as-code tool (v1.5+).
-   **Git**: To clone the repository.
-   An **AWS account** with billing enabled.
-   A **Cloudflare account** with the domain `study-amigo.app` already registered.

---

## 2. AWS Account Setup & CLI Credentials

Terraform needs programmatic access to your AWS account. You will create an IAM user with the necessary permissions and configure the AWS CLI with its credentials.

### 2.1. Create an IAM User

1.  Log in to the **AWS Management Console**: [https://console.aws.amazon.com/](https://console.aws.amazon.com/)
2.  Navigate to **IAM** (Identity and Access Management):
    -   Search for "IAM" in the top search bar, or go to `Services > Security, Identity, & Compliance > IAM`.
3.  In the left sidebar, click **Users**, then click **Create user**.
4.  **User name**: Enter `terraform-deployer` (or any name you prefer).
5.  Click **Next**.
6.  **Set permissions**:
    -   Select **Attach policies directly**.
    -   Search for and check the following policies:
        -   `AmazonEC2FullAccess`
        -   `AmazonVPCFullAccess`
    -   For a production setup, you would create a custom policy with least-privilege permissions. These broad policies are acceptable for a personal project.
7.  Click **Next**, then **Create user**.

### 2.2. Create Access Keys

1.  Click on the newly created user (`terraform-deployer`).
2.  Go to the **Security credentials** tab.
3.  Under **Access keys**, click **Create access key**.
4.  Select **Command Line Interface (CLI)** as the use case.
5.  Check the confirmation checkbox and click **Next**.
6.  (Optional) Add a description tag, then click **Create access key**.
7.  **IMPORTANT**: Copy or download the **Access key ID** and **Secret access key** now. The secret key will not be shown again.

### 2.3. Configure the AWS CLI

Open a terminal on your local machine and run:

```bash
aws configure
```

Enter the following when prompted:

```
AWS Access Key ID [None]: <paste your Access Key ID>
AWS Secret Access Key [None]: <paste your Secret Access Key>
Default region name [None]: us-east-1
Default output format [None]: json
```

### 2.4. Verify the CLI Configuration

```bash
aws sts get-caller-identity
```

You should see output like:

```json
{
    "UserId": "AIDAXXXXXXXXXXXXXXXXX",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/terraform-deployer"
}
```

---

## 3. Install Terraform

### macOS (Homebrew)

```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

### Ubuntu/Debian

```bash
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

### Verify

```bash
terraform -version
```

---

## 4. Generate an SSH Key Pair

You need an SSH key pair to access the EC2 instance. If you already have one you want to use, skip this step.

```bash
ssh-keygen -t ed25519 -C "study-amigo-aws" -f ~/.ssh/study-amigo-aws
```

-   Press Enter to accept defaults (or set a passphrase for extra security).
-   This creates two files:
    -   `~/.ssh/study-amigo-aws` (private key - keep this safe)
    -   `~/.ssh/study-amigo-aws.pub` (public key - Terraform will upload this to AWS)

---

## 5. Configure Terraform Variables

1.  Navigate to the Terraform directory:

    ```bash
    cd server/aws_terraform
    ```

2.  Copy the example variables file:

    ```bash
    cp terraform.tfvars.example terraform.tfvars
    ```

3.  Edit `terraform.tfvars` with your values:

    ```bash
    # Edit with your preferred editor
    nano terraform.tfvars
    ```

    At minimum, you must set:

    ```hcl
    ssh_public_key_path = "~/.ssh/study-amigo-aws.pub"
    flask_secret_key    = "your_generated_secret_key_here"
    ```

    Generate a Flask secret key:

    ```bash
    python3 -c 'import secrets; print(secrets.token_hex(24))'
    ```

---

## 6. Deploy Infrastructure with Terraform

### 6.1. Initialize Terraform

```bash
cd server/aws_terraform
terraform init
```

This downloads the AWS provider plugin and initializes the working directory.

### 6.2. Preview the Changes

```bash
terraform plan
```

Review the output. Terraform will show you every resource it plans to create:
-   1 VPC
-   1 Subnet
-   1 Internet Gateway
-   1 Route Table
-   1 Security Group (with HTTP, SSH inbound rules)
-   1 EC2 instance (t4g.micro)
-   1 Elastic IP

### 6.3. Apply the Configuration

```bash
terraform apply
```

-   Type `yes` when prompted to confirm.
-   Wait 3-5 minutes for the infrastructure to be created and the user_data bootstrap script to finish.

### 6.4. Note the Outputs

After successful apply, Terraform will print:

```
Outputs:

instance_id       = "i-0abc123def456..."
public_ip         = "54.xxx.xxx.xxx"
elastic_ip        = "3.xxx.xxx.xxx"
ssh_command       = "ssh -i ~/.ssh/study-amigo-aws ubuntu@3.xxx.xxx.xxx"
```

**Save the `elastic_ip` value** - you need it for the Cloudflare DNS step.

### 6.5. Wait for Bootstrap to Complete

The EC2 instance runs a user_data script on first boot that installs Docker, clones the repo, and starts the containers. This takes approximately 3-5 minutes after the instance is reported as running.

SSH into the instance to monitor progress:

```bash
ssh -i ~/.ssh/study-amigo-aws ubuntu@<elastic_ip>

# Watch the cloud-init log in real time
tail -f /var/log/cloud-init-output.log

# Check if Docker containers are running
sudo docker compose -f /opt/study-amigo/docker-compose.yml ps
```

---

## 7. Configure Cloudflare DNS

1.  Log in to [Cloudflare Dashboard](https://dash.cloudflare.com/).
2.  Select the `study-amigo.app` domain.
3.  Go to **DNS > Records**.
4.  Add the following records:

    | Type | Name | Content | Proxy Status | TTL |
    |------|------|---------|-------------|-----|
    | A    | `@`  | `<elastic_ip>` | **Proxied** (orange cloud) | Auto |
    | A    | `www`| `<elastic_ip>` | **Proxied** (orange cloud) | Auto |

5.  Click **Save** for each record.

---

## 8. Configure Cloudflare SSL Settings

Since Cloudflare is handling SSL termination and the EC2 instance runs plain HTTP:

1.  In the Cloudflare dashboard, go to **SSL/TLS > Overview**.
2.  Set the encryption mode to **Flexible**.
    -   This means: Browser ↔ Cloudflare uses HTTPS, Cloudflare ↔ EC2 uses HTTP.
    -   This is acceptable for a personal/small-scale app. For stricter security, use "Full" mode and install a Cloudflare Origin Certificate on the EC2 instance.

3.  Go to **SSL/TLS > Edge Certificates**.
4.  Ensure **Always Use HTTPS** is enabled (redirects HTTP to HTTPS).

---

## 9. Verify the Deployment

### 9.1. Direct IP Test (before DNS propagation)

```bash
# Test that the EC2 instance responds
curl http://<elastic_ip>/

# Test API endpoint
curl -X POST http://<elastic_ip>/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass12345","name":"Test User"}'
```

### 9.2. Domain Test (after DNS propagation, usually 1-5 minutes)

Open your browser and navigate to:

-   `https://study-amigo.app` - Should show the React application.
-   `https://www.study-amigo.app` - Should also work.

### 9.3. Full Functional Test

1.  Register a new user.
2.  Log in.
3.  Create a deck.
4.  Add cards to the deck.
5.  Start a review session.

---

## 10. Purchase a Reserved Instance (Cost Optimization)

**Do this after you have confirmed everything works.** The Reserved Instance is a billing discount that applies automatically to your running On-Demand instance.

1.  Go to the **AWS Console** > **EC2** > **Reserved Instances** (left sidebar).
2.  Click **Purchase Reserved Instances**.
3.  Configure:
    -   **Platform**: Linux/UNIX
    -   **Instance Type**: `t4g.micro`
    -   **Tenancy**: Default
    -   **Term**: 1 year
    -   **Payment Option**: Choose one:
        -   **No Upfront**: ~$4.10/month (billed monthly, no commitment beyond 1 year)
        -   **All Upfront**: ~$43/year (~$3.58/month effective, cheapest overall)
        -   **Partial Upfront**: A middle ground
4.  Click **Search** to see available offerings, then **Purchase**.

The discount is applied automatically to your running `t4g.micro` instance in `us-east-1`. No changes to Terraform or the instance are needed.

---

## 11. Ongoing Operations

### SSH Access

```bash
ssh -i ~/.ssh/study-amigo-aws ubuntu@<elastic_ip>
```

### View Application Logs

```bash
ssh -i ~/.ssh/study-amigo-aws ubuntu@<elastic_ip>

# Docker container logs
sudo docker compose -f /opt/study-amigo/docker-compose.yml logs -f
sudo docker compose -f /opt/study-amigo/docker-compose.yml logs -f server
sudo docker compose -f /opt/study-amigo/docker-compose.yml logs -f client
```

### Update the Application

To deploy a new version of the code:

```bash
ssh -i ~/.ssh/study-amigo-aws ubuntu@<elastic_ip>

cd /opt/study-amigo
sudo git pull origin main
sudo docker compose build
sudo docker compose up -d
```

### Backup SQLite Databases

```bash
# From your local machine - download backups
scp -i ~/.ssh/study-amigo-aws ubuntu@<elastic_ip>:/opt/study-amigo/server/admin.db ./backup_admin.db
scp -i ~/.ssh/study-amigo-aws -r ubuntu@<elastic_ip>:/opt/study-amigo/server/user_dbs/ ./backup_user_dbs/
```

### EBS Snapshot (Full Disk Backup)

1.  Go to **AWS Console** > **EC2** > **Volumes**.
2.  Select your volume, click **Actions** > **Create Snapshot**.
3.  Cost: ~$0.05/GB-month (~$1/month for a 20GB snapshot).

### Restart Containers

```bash
ssh -i ~/.ssh/study-amigo-aws ubuntu@<elastic_ip>

sudo docker compose -f /opt/study-amigo/docker-compose.yml restart
```

---

## 12. Terraform Script Structure

The Terraform scripts are located in `server/aws_terraform/` and organized as follows:

```
server/aws_terraform/
├── main.tf                    # Core infrastructure resources
├── variables.tf               # Input variable declarations
├── outputs.tf                 # Output values (IP, SSH command, etc.)
├── user_data.sh               # Bootstrap script run on first EC2 boot
├── terraform.tfvars.example   # Example variable values (safe to commit)
├── terraform.tfvars           # Your actual variable values (DO NOT COMMIT)
└── .gitignore                 # Ignores state files and secrets
```

### File Descriptions

| File | Purpose |
|------|---------|
| `main.tf` | Defines all AWS resources: VPC, subnet, internet gateway, route table, security group, EC2 instance, and Elastic IP. Uses the `user_data.sh` script for instance bootstrap. |
| `variables.tf` | Declares all configurable variables with descriptions, types, and default values. Sensitive values (like `flask_secret_key`) are marked as sensitive. |
| `outputs.tf` | Defines values printed after `terraform apply`: the Elastic IP, instance ID, and a ready-to-use SSH command. |
| `user_data.sh` | Bash script executed automatically on the EC2 instance's first boot. Installs Docker, clones the StudyAmigo repo, configures the Flask `.env` file, adjusts `docker-compose.yml` for port 80, and starts the containers. |
| `terraform.tfvars.example` | Template showing which variables need values. Copy to `terraform.tfvars` and fill in. |
| `.gitignore` | Prevents Terraform state files (`*.tfstate`), local plugin cache (`.terraform/`), and secrets (`terraform.tfvars`) from being committed. |

### What `main.tf` Creates

1.  **VPC** (`10.0.0.0/16`): An isolated virtual network for the application.
2.  **Public Subnet** (`10.0.1.0/24`): A subnet with internet access in `us-east-1a`.
3.  **Internet Gateway**: Allows the subnet to reach the internet.
4.  **Route Table**: Routes all outbound traffic (`0.0.0.0/0`) through the internet gateway.
5.  **Security Group**: Allows inbound SSH (port 22) and HTTP (port 80). All outbound traffic is allowed.
6.  **EC2 Key Pair**: Your public SSH key, uploaded to AWS for instance access.
7.  **EC2 Instance** (`t4g.micro`): ARM-based instance running Ubuntu 24.04 LTS, with a 20GB gp3 EBS volume. Bootstrapped by `user_data.sh`.
8.  **Elastic IP**: A static public IPv4 address attached to the instance.

### What `user_data.sh` Does on First Boot

1.  Updates system packages.
2.  Installs Docker and Docker Compose plugin.
3.  Clones the `StudyAmigoApp` repository to `/opt/study-amigo`.
4.  Writes the Flask `SECRET_KEY` to `server/.env`.
5.  Updates `docker-compose.yml` to expose port 80 (instead of 8080).
6.  Updates Flask CORS settings to allow `https://study-amigo.app`.
7.  Builds and starts Docker containers via `docker compose up -d`.

---

## 13. Tear Down

To destroy all AWS resources created by Terraform:

```bash
cd server/aws_terraform
terraform destroy
```

-   Type `yes` when prompted.
-   This removes the EC2 instance, Elastic IP, VPC, and all associated resources.
-   **Warning**: This permanently deletes all data on the instance (including SQLite databases). Back up first!
-   Remember to also remove the DNS records from Cloudflare manually.
-   If you purchased a Reserved Instance, it **cannot be cancelled**. The billing discount will continue for the full term, but without a running instance to apply to.
