# **Deploy Guide**

## **Options**
I've included two deployment automations that are mutually independent. The options are:
1) python script / jupyter with functions that take advantege of `subprocess` module and `gcloud` commands
2) terraform script that can be executed within cloud shell editor

## **What resources are being deployed?**
- artifact registry reposiory
- three service accounts: deployment, cloud run operations, cloud run/functions invoker. Each is assigned required permissions/roles
- cloud build trigger based on cloudbuild.yaml and deployment SA. 
- bigquery datasets: monitoring, experiments
- cloud storage bucket: experiments-bucket
- 

## **Deploy Cloud Run**
Cloud Run service can be deployed by:
- using a function `func_name` from deploy.py 
- manually invoking the trigger 
- pushing to repo (if used as template)


## *Differnces between methods**
Right now, terraform script does not support creation of all assets.

