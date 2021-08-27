# Capstone
This project is a microserviced expense report with separate services for backend logic, user authentication, packet routing, and the frontend.

## Setup and Deployment
All containers are all automatically built through travis-ci and pushed to the following repositories: [frontend](https://hub.docker.com/repository/docker/samcowley/udacity-capstone-frontend), [backend](https://hub.docker.com/repository/docker/samcowley/udacity-capstone-backend), [proxy](https://hub.docker.com/repository/docker/samcowley/udacity-capstone-proxy), [auth](https://hub.docker.com/repository/docker/samcowley/udacity-capstone-auth)

In AWS, a user needs access to a Postgres RDS instance, a S3 instance, and an EKS instance.
With the deployment files, the following `secrets.yaml` needs to be created and applied:

```
apiVersion: v1
kind: Secret
metadata:
  name: secrets
type: Opaque
data:
  session_secret: VALUE
  auth0_client_id: VALUE
  auth0_client_secret: VALUE
  auth0_api_base_url: VALUE
  auth0_access_token_url: VALUE
  auth0_authorize_url: VALUE
  s3_bucket: VALUE
  s3_region: VALUE
  s3_timeout: VALUE
  rds_endpoint: VALUE
  rds_port: VALUE
  rds_db: VALUE
  rds_user: VALUE
  rds_pass: VALUE
  rds_region: VALUE
```

Auth0 requires a callback url to be defined, so it must match the endpoint or authentication will fail.

## Rolling Updates
Updates through EKS are rolling updates by default. The older versions of containers are not deleted until the new version
has succesfully started.

## A/B Testing
Deploying the containers to a new namespace and updating the DNS entry will provide A/B Testing requirements.
With both instances running with their own endpoints, DNS can point to each one as <domain> and old.<domain>

A running example of this is https://www.reddit.com

Since their website redesign, both designs can be accessed via https://wwww.reddit.com (latest) or https://old.reddit.com (old)

## Monitoring
Monitoring is handled by fluent-bit and sent to CloudWatch. All output logs for the containers are sent to CloudWatch.

## Testing the application
All endpoints are available through the frontend container.
A user should be able to:
* create, delete, and update expense reports.
* create, delete, and update expense items.
* upload, download, and delete images tied to an expense item.
* Only able to view reports and expenses tied to that specific user.

### Notes
Only the "Category" field of expense reports are allowed to be empty.
