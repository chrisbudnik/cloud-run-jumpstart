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
        print(f"Failed to create build trigger: {e.stderr}")
        return None
    
    except json.JSONDecodeError:
        print(f"Failed to parse JSON output: {result.stdout}")
        return None
    

def create_artifact_repository(
        project_id: str, location: str, repository_name: str
    ) -> dict | None:
    """
    Create a Docker repository in Google Artifact Registry.
    """
    
    command = [
        "gcloud", "artifacts", "repositories", "create", repository_name,
        "--repository-format=docker",
        "--location", location,
        "--project", project_id,
        "--format=json"
    ]
    result = run_command(command)

    # Check if the repository was created successfully
    if result:
        print(f"Repository '{repository_name}' created successfully.")

    return result


def create_service_account(project_id, service_account_name, display_name):
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
    account_email = f"{service_account_name}@{project_id}.iam.gserviceaccount.com"
    
    # Add the service account email to the result
    result["account_email"] = account_email
    return account_email


def assign_roles_to_service_account(
        project_id: str, service_account_email: str, roles: list[str]
    ) -> dict | None:
    """
    Assign roles to a service account.
    """
    for role in roles:
        add_role_command = [
            "gcloud", "projects", "add-iam-policy-binding", project_id,
            "--member", f"serviceAccount:{service_account_email}",
            "--role", role
        ]
        result = run_command(add_role_command)

        # Check if roles were granted successfully
        if result:
            print(f"Role '{role}' assigned to service account '{service_account_email}' successfully.")
        

def create_service_account_with_permissions(project_id, service_account_name, display_name, roles):
    """
    Create a service account and assign roles.
    """
    # Create the service account
    account_email = create_service_account(project_id, service_account_name, display_name)

    # Assign roles to the service account
    assign_roles_to_service_account(project_id, account_email, roles)


def create_cloud_build_trigger(
        project_id: str, 
        repo_name: str,      # github repo name 
        repo_owner: str,     # github account 
        trigger_name: str, 
        region: str, 
        service_account_email: str = "", 
        config_yaml: str = "cloudbuild.yaml",    
         
        
        #tags
    ) -> dict | None:

    """Create a Cloud Build trigger for a GitHub repository."""

    command = [
        "gcloud", "builds", "triggers", "create", "github",
        "--repo-name", repo_name,
        "--repo-owner", repo_owner,
        "--branch-pattern", "^main$",
        "--build-config", config_yaml,
        "--name", trigger_name,
        "--region", region,
        #"--service-account", service_account_email,
        "--project", project_id,
        "--format=json"
    ]
    
    # Add the service account email if provided
    if service_account_email:
        command.extend(["--service-account", service_account_email])
    
    run_command(command)




