variable "project_id" {
  description = "ID of the GCP project to deploy into."
  type        = string
  default     = "ribal-contact-478509-c3"
}

variable "region" {
  description = "GCP region for resources."
  type        = string
  default     = "europe-west1"
}

variable "zone" {
  description = "GCP zone for the compute instance."
  type        = string
  default     = "europe-west1-b"
}

variable "instance_name" {
  description = "Name of the compute instance."
  type        = string
  default     = "etl-e2-standard4"
}

variable "machine_type" {
  description = "GCP machine type for the instance."
  type        = string
  default     = "e2-standard-4"
}

variable "boot_image" {
  description = "Boot image for the instance (project/image-family or self link)."
  type        = string
  default     = "debian-cloud/debian-11"
}

variable "tags" {
  description = "Network tags to apply to the instance."
  type        = list(string)
  default     = ["docker-host"]
}

variable "start_schedule_cron" {
  description = "Cron schedule (in Cloud Scheduler format) for starting the VM."
  type        = string
  # Default: every day at 12:00 (noon)
  default = "0 12 * * *"
}

variable "start_schedule_time_zone" {
  description = "IANA time zone for the start schedule (e.g. Europe/Paris)."
  type        = string
  default     = "Europe/Paris"
}
