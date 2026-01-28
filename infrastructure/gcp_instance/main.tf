terraform {
  required_version = ">= 1.3.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

resource "google_compute_resource_policy" "docker_vm_start_schedule" {
  name   = "${var.instance_name}-start-schedule"
  region = var.region

  instance_schedule_policy {
    time_zone = var.start_schedule_time_zone

    vm_start_schedule {
      # Cron schedule: default is every day at noon
      schedule = var.start_schedule_cron
    }
  }
}

resource "google_compute_instance" "docker_vm" {
  name         = var.instance_name
  machine_type = var.machine_type
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = var.boot_image
      size  = 50
      type  = "pd-balanced"
    }
  }

  network_interface {
    # Use the default network by default; customize if needed.
    network = "default"

    # Ephemeral external IP so you can SSH directly.
    access_config {}
  }

  # Startup script will install Docker on first boot.
  metadata_startup_script = file("${path.module}/startup.sh")

  tags = var.tags

  # Attach the start schedule resource policy so the VM starts daily at noon.
  resource_policies = [google_compute_resource_policy.docker_vm_start_schedule.self_link]
}
