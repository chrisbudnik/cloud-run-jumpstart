# How to configure cloudbuild.yaml

| Parameter | Description |
|-----------|-------------|
| id | A unique identifier for this step in the Cloud Build process. It helps in referencing and organizing build steps. |
| name | Specifies the Docker image to be used for executing this build step. In this case, it's using the Google Cloud SDK image. |
| run deploy | The command to deploy a new Cloud Run service or update an existing one. It's followed by the service name. |
| --region | Defines the geographical location where the Cloud Run service will be deployed. This should typically match the region of other related resources. |
| --service-account | Specifies the Google Cloud service account that the Cloud Run service will use to authenticate and authorize actions. This account should have the necessary permissions for the service's operations. |
| --image | Indicates the full path to the container image in Artifact Registry that will be deployed to Cloud Run. |
| --port | Specifies the port number that the container will listen on for incoming requests. |
| --cpu | Defines the number of CPU units to allocate to each instance of the service. |
| --memory | Sets the amount of memory to allocate to each instance of the service. |
| --min-instances | Configures the minimum number of instances to run at all times, even when there's no traffic. Used for auto-scaling. |
| --max-instances | Sets the maximum number of instances that can be created during high-traffic periods. Also used for auto-scaling. |
| --timeout | Defines the maximum duration (in seconds) that Cloud Run will wait for a request to be processed before terminating it. |
| --concurrency | Specifies the maximum number of simultaneous requests that can be processed by a single instance. |
| --allow-unauthenticated | When present, allows the service to be accessed without authentication. If omitted or set to '--no-allow-unauthenticated', the service requires authentication. |
| --set-secrets | Used to configure environment variables that are populated with the values of Cloud Secrets. |
| --set-env-vars | Allows setting of environment variables that will be available to the running container. |
| --ingress | Configures how the service can be accessed. Options include 'all', 'internal', and 'internal-and-cloud-load-balancing'. |
| --platform | Specifies the underlying infrastructure for running the Cloud Run service. 'managed' indicates serverless infrastructure managed by Google Cloud. |