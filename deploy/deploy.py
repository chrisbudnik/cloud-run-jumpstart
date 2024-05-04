import json
import subprocess

def run_command(command: list[str]) -> dict | None:
    """
    Utility function to run a command and return JSON output.
    """

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return json.loads(result.stdout) if result.stdout else None

    except subprocess.CalledProcessError as e:
        print(f"Failed to execute gcloud command: {e.stderr}")
        return
    
    except json.JSONDecodeError:
        print(f"Failed to parse JSON output: {result.stdout}")
        return


def create_artifact_repository(
        project_id: str, location: str, docker_repository_name: str
    ) -> dict | None:
    """
    Create a Docker repository in Google Artifact Registry.
    """
    
    command = [
        "gcloud", "artifacts", "repositories", "create", docker_repository_name,
        "--repository-format=docker",
        "--location", location,
        "--project", project_id,
        "--format=json"
    ]
    result = run_command(command)

    # Check if the repository was created successfully
    if not result:
        raise NameError(
            f"Failed to create Docker repository '{docker_repository_name}'"
            " - check if it already exists."
            )

    print(f"Docker epository '{docker_repository_name}' created successfully.")

    return result


def create_service_account(
        project_id: str, service_account_name: str, display_name: str
    ) -> dict:
    """
    Create a service account.
    """
    # Create the service account
    create_account_command = [
        "gcloud", "iam", "service-accounts", "create", service_account_name,
        "--display-name", display_name,
        "--project", project_id,
        "--format=json"
    ]

    # Build the service account
    result = run_command(create_account_command)

    if not result:
        raise NameError(
            f"Failed to create service account '{service_account_name}'"
            " - check if it already exists."
            )
    
    account_email = f"{service_account_name}@{project_id}.iam.gserviceaccount.com"
    
    # Add the service account email to the result
    result["account_email"] = account_email
    return result


def assign_roles_to_service_account(
        project_id: str, service_account_email: str, roles: list[str]
    ) -> dict | None:
    """
    Assign roles to a service account.
    """
    results = []
    for role in roles:
        add_role_command = [
            "gcloud", "projects", "add-iam-policy-binding", project_id,
            "--member", f"serviceAccount:{service_account_email}",
            "--role", role,
            "--condition=None",
            "--format=json",
        ]
        result = run_command(add_role_command)

        # Check if roles were granted successfully
        results.append(result)
    
    if all([item is not None for item in results]):
        print(f"Roles [{','.join(roles)}] assigned to service account '{service_account_email}' successfully.")
    
    else:
        error_roles = [role for role, result in zip(roles, results) if result is None]
        raise NameError(f"Failed to assign roles: {", ".join(error_roles)} to the service account.")

    return results
        

def create_service_account_with_permissions(
        project_id: str, service_account_name: str, display_name: str, roles: list[str]
    ) -> str:
    """
    Create a service account and assign roles.
    """
    # Create the service account
    account = create_service_account(project_id, service_account_name, display_name)
    account_email = account.get("account_email")

    # Assign roles to the service account
    if roles and account_email:
        assign_roles_to_service_account(project_id, account_email, roles)
    else: 
        print("No roles were assigned to the service account.")

    return account_email


def create_cloud_build_trigger(
        project_id: str, 
        repo_name: str, 
        repo_owner: str,
        repo_connection: str,
        trigger_name: str, 
        config_yaml: str = "cloudbuild.yaml", 
        region: str = "us-central1",  
        service_account_email: str = "", 
    ) -> dict | None:

    """Create a Cloud Build trigger for a GitHub repository."""
    
    repository = f"projects/{project_id}/locations/{region}/connections/{repo_connection}/repositories/{repo_owner}-{repo_name}"

    command = [
        "gcloud", "builds", "triggers", "create", "github",
        "--repository", repository,
        "--branch-pattern", "^main$",
        "--build-config", config_yaml,
        "--name", trigger_name,
        "--region", region,
        "--service-account", service_account_email,
        "--project", project_id,
        "--format=json"
    ]

    if service_account_email:
        service_account = f"projects/{project_id}/serviceAccounts/{service_account_email}"
        command.extend(["--service-account", service_account])

    result = run_command(command)

    if not result:
        raise NameError(
            f"Failed to create cloud build trigger '{trigger_name}'"
            " - check if it already exists."
            )


def main(
        project_id: str, 
        location: str, 
        docker_repo_name: str, 
        repo_name: str, 
        repo_owner: str, 
        region: str, 
    ) -> None:
    
    # Create a Docker repository in Google Artifact Registry
    create_artifact_repository(project_id, location, docker_repo_name)

    # Create service account: cloud-run-operations
    roles_operations = [
        "roles/bigquery.jobUser",    
        "roles/bigquery.dataViewer",  
        "roles/viewer",               
        "roles/storage.admin",        
    ]

    service_account_ops = create_service_account_with_permissions(
        project_id, 
        service_account_name = "sa-cloud-run-operations", 
        display_name = "Service account for Cloud Run management and internal operations.", 
        roles=roles_operations
    )
    
    # Create service account: cloud-run-deployment
    roles_deployment = [
        "roles/artifactregistry.writer",
        "roles/run.admin",
        "roles/logging.logWriter",
        "roles/iam.serviceAccountUser",
        "roles/source.reader"
    ]

    service_account_deploy = create_service_account_with_permissions(
        project_id, 
        service_account_name = "sa-cloud-run-deployment", 
        display_name = "Service account for Cloud Build to deploy Cloud Run apps.", 
        roles=roles_deployment
    )


    # Create a Cloud Build trigger
    create_cloud_build_trigger(
        project_id=project_id, 
        repo_name=repo_name, 
        repo_owner=repo_owner, 
        trigger_name="cloud-run-jumpstart-deploy", 
        region=region,
        service_account_email=service_account_deploy, 
        config_yaml="cloudbuild.yaml"
    )

    

if __name__ == "__main__":
    main(
        project_id = "chris-sandbox-2023",
        location = "us-central1",
        docker_repo_name = "cloud-run-docker-images",
        repo_name = "cloud-run-jumpstart",
        repo_owner = "chrisbudnik",
        region = "us-central1"
    )