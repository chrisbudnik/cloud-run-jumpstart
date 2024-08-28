# How to configure cloudbuild.yaml

Here's an MD table explaining each parameter from the provided CloudBuild YAML fragment:

| Parameter | Values | Description |
|-----------|--------|-------------|
| id | "Deploy Cloud Run Service" | Identifier for the deployment step |
| name | 'gcr.io/cloud-builders/gcloud:latest' | Docker image used for deployment |
| run deploy | 'cloud-run-jumpstart' | Command to deploy a Cloud Run service with the specified name |
| --region | 'us-central1' | Specifies the region for deployment |
| --service-account | 'sa-cloud-run-operations@${PROJECT_ID}.iam.gserviceaccount.com' | Service Account used by the Cloud Run service |
| --image | 'us-central1-docker.pkg.dev/${PROJECT_ID}/cloud-run-docker-images/cloud-run-jumpstart-img' | Location of the container image in Artifact Registry |
| --port | '8080' | Container port to listen on |
| --cpu | '1' | Number of CPUs allocated to each instance |
| --memory | '256Mi' | Memory allocated to each instance |
| --min-instances | '0' | Minimum number of instances for auto-scaling |
| --max-instances | '1' | Maximum number of instances for auto-scaling |
| --timeout | '30' | Maximum request handling time in seconds |
| --concurrency | '80' | Maximum number of requests per container instance |
| --allow-unauthenticated | N/A | Allows unauthenticated access to the service |
| --set-secrets | 'ACCESS_KEY=access-key:latest' | Sets up environment secrets |
| --set-env-vars | 'ENV_VAR=example_value' | Sets up environment variables |
| --ingress | 'all' | Configures network ingress settings |
| --platform | 'managed' | Specifies the deployment platform |