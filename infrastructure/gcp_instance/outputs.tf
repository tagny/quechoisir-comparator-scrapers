output "instance_name" {
  description = "Name of the created instance."
  value       = google_compute_instance.docker_vm.name
}

output "instance_self_link" {
  description = "Self link of the created instance."
  value       = google_compute_instance.docker_vm.self_link
}

output "instance_external_ip" {
  description = "External IP address of the instance."
  value       = google_compute_instance.docker_vm.network_interface[0].access_config[0].nat_ip
}
