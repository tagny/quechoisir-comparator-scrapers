# GCP ETL Compute Instance (Terraform)

This directory contains Terraform configuration for a single Google Compute Engine VM that runs the ETL workload.

## What this module creates

- A Google provider configured with:
  - `project_id` (GCP project ID)
  - `region`
  - `zone`
- A `google_compute_instance` named via `var.instance_name` with:
  - Boot disk based on `var.boot_image` (default: `debian-cloud/debian-11`)
  - Machine type controlled by `var.machine_type` (default: `e2-standard-4`)
  - Ephemeral external IP on the default network
  - `metadata_startup_script` pointing to `startup.sh` (installs Docker and prepares the VM)
  - Network tags from `var.tags` (default: `["docker-host"]`)
- A `google_compute_resource_policy` that schedules the VM to **start daily at noon** using an instance schedule policy.

## Inputs

See `variables.tf` for full details. Key variables:

- `project_id` (string, **required**): GCP project ID.
- `region` (string, default `europe-west1`): Region for resources.
- `zone` (string, default `europe-west1-b`): Zone for the VM.
- `instance_name` (string, default `etl-e2-standard4`): Name of the VM.
- `machine_type` (string, default `e2-standard-4`): Compute Engine machine type.
- `boot_image` (string, default `debian-cloud/debian-11`): Image or family for the boot disk.
- `tags` (list(string), default `["docker-host"]`): Network tags applied to the instance.
- `start_schedule_cron` (string, default `"0 12 * * *"`): Cron for daily start time.
- `start_schedule_time_zone` (string, default `"Europe/Paris"`): IANA time zone for the schedule.

## Usage

1. Ensure you have authenticated with `gcloud` and that the Google Cloud SDK and Terraform are installed.
2. Set your `project_id` (either via `terraform.tfvars`, environment, or CLI).

Example `terraform.tfvars`:

```hcl
project_id        = "your-gcp-project-id"
region            = "europe-west1"
zone              = "europe-west1-b"
instance_name     = "etl-e2-standard4"
machine_type      = "e2-standard-4"
boot_image        = "debian-cloud/debian-11"
start_schedule_cron      = "0 12 * * *"     # every day at noon
start_schedule_time_zone = "Europe/Paris"   # adjust as needed
tags = [
  "docker-host",
]
```

Then from this directory:

```bash
terraform init
terraform plan
terraform apply
```

## Notes

- The instance schedule only controls **automatic starts**; stopping or shutting down the VM remains your responsibility (e.g. via scripts, schedules, or manual actions).
- Update `startup.sh` if you need additional software or bootstrap logic on the VM.
