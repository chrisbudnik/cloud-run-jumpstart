provider "google" {
  project = "chris-sandbox-2023"
  region  = "us-central1"
}

# Define local variables
locals {
  project         = "chris-sandbox-2023"
  region          = "us-central1"
  repo_connection = "chris-github-connection"
  repo_owner      = "chrisbudnik"
  repo_name       = "cloud-run-jumpstart"

  roles_operations = [
    "roles/bigquery.jobUser",
    "roles/bigquery.dataViewer",
    "roles/viewer",
    "roles/storage.admin"
  ]
  roles_deployment = [
    "roles/artifactregistry.writer",
    "roles/run.admin",
    "roles/logging.logWriter",
    "roles/iam.serviceAccountUser",
    "roles/source.reader"
  ]
}

# Create a Docker repository in Google Artifact Registry
resource "google_artifact_registry_repository" "docker_repo" {
  location      = "us-central1"
  repository_id = "cloud-run-docker-images-tf"
  format        = "DOCKER"

  labels = {
    environment = "production"
  }
}

# Create service accounts for operations and deployment
resource "google_service_account" "service_account" {
  for_each = toset(["operations-tf", "deployment-tf"])

  project      = "chris-sandbox-2023"
  account_id   = "sa-cloud-run-${each.key}"
  display_name = "Service Account for Cloud Run ${each.key}"
}

# Create IAM members for "operations"
resource "google_project_iam_member" "iam_member_ops" {
  for_each = toset(local.roles_operations)

  project = "chris-sandbox-2023"
  role    = each.value
  member  = "serviceAccount:${google_service_account.service_account["operations-tf"].email}"
}

# Create IAM members for "deployment"
resource "google_project_iam_member" "iam_member_deploy" {
  for_each = toset(local.roles_deployment)

  project = "chris-sandbox-2023"
  role    = each.value
  member  = "serviceAccount:${google_service_account.service_account["deployment-tf"].email}"
}
