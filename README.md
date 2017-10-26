# RDSS Pure Adaptor

A per-institution adaptor for installations of the [Pure research information system](https://www.elsevier.com/solutions/pure). This adaptor periodically polls the datasets endpoint of a Pure installation, fetching new and modified datasets, and relaying these datasets on to the Jisc Research Data Shared Service (RDSS). At present the RDSS Pure Adaptor can interact with version 5.9 of the Pure API, but is designed to easily accommodate interaction with other versions of the API in future.  

### Language / Framework
- Python 3.6+

### Service Infrastructure

- dev
- uat
- prod

#### Sub-Services

The RDSS Pure Adaptor depends on the following infrastructure:
- AWS Kinesis Streams
- AWS DynamoDB
- AWS S3 Buckets
- AWS EC2 Clusters


(##configuration)
The RDSS Pure Adaptor requires that the following environment variables are set:

- `PURE_API_VERSION`

   A string description of the Pure API version being targeted. Used to select the Pure API integration used by the RDSS Pure Adaptor.

- `PURE_API_URL`

   The url of the Pure API endpoint.

- `PURE_API_KEY`

   The api key which is used to authorise access to the Pure API endpoint.

- `INSTANCE_ID`

   A string describing the institution and environment which this instance of the RDSS Pure Adaptor is targeting, e.g. `pure-adaptor-<jisc_id>-<env>`. This is the name of the DynamoDB table used to store the state of the adaptor, as well as the name of the s3 bucket which the adaptor will upload downloaded datasets.

- `RDSS_INTERNAL_INPUT_QUEUE`

   The name of the RDSS internal input queue to which the Pure Adaptor will write messages.

- `RDSS_MESSAGE_INVALID_QUEUE`

   The name of the RDSS invalid message queue to which the Pure Adaptor will write invalid messages.

- `RDSS_MESSAGE_ERROR_QUEUE`

   The name of the RDSS error message queue to which the Pure Adaptor will write error messages.

In addition to the aforementioned variables, the following environment variables are also required by the `boto3` library to access the AWS resources utilised by the RDSS Pure Adaptor:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`

---------------------------------------------------------

## Deployment

The RDSS Pure Adaptor is intended to be deployed as a service on a per-institution and per-environment basis as part of the RDSS institutional ECS clusters infrastructure. This repository is targeted by a build task defined in the [RDSS Institutional ECS Clusters](https://github.com/JiscRDSS/rdss-institutional-ecs-clusters) repository. This task will build the Docker image defined by the [Dockerfile](/Dockerfile) in this repository. The RDSS Pure Adaptor is provided as a generic docker image which is configured by the environmental variables outlined in the [Configuration](##configuration) section.

### Setup

> E.g. Creating a terraform state bucket.
> ```
> aws s3 mb --region eu-west-2 s3://rdss-new-service-jenkins
> ```
>
> #### Inspect remote state
> ```
> aws s3 cp s3://rdss-new-service-jenkins/env:/xxx/terraform.tfstate .
> ```
>
>Create `.env` file needed for deployment:
> ```
> cp .env.example .env
> ```
> Update variables in `.env`, eg `$DB_PASSWORD` etc.


### Deploy
> E.g.
> ```
> ./bin/deploy
> ```

---------------------------------------------------------

## Test
- Create testing configurations
- Automated tests
- Manual Tests

---------------------------------------------------------

## Dcoumentation
> Documentation for the new service

### FAQ
> A list of frequently asked questions and answers. Any gotchas should also be listed.

### References (Optional)
> A list of any relevant reference documents (hyperlinks).
---------------------------------------------------------

## Developer Setup
> Remove this section and subsections if it is not applicable for the new service.

E.g.
 - Create a virtualenv then install requirements
 - Run Server in Development mode
 - Upload or migrate testing data

---------------------------------------------------------

## Jenkins
> Remove this section and subsections if it is not applicable for the new service.

### Vagrant
1. Make sure config contains relevant to your box configuration
2. Setup vagrant box `vagrant up`
3. Run installation process by opening http://192.168.33.10:8080/
(or other configured address) and follow instructions
4. Set credentials - see below
5. Create pipeline job
6. Configure pipeline job - set Definition - select "Pipeline script from SCM" option
7. Set SCM branch to `feature/your-rdss-branch-jobs` - it will automatically pick up the Jenkinsfile in the root of the repository

### Setting up credentials
>Any passwords, passphrases, SSH keys, authentication or encryption based tokens used **must** be provided to RDSS administrators (i.e. @danielgrant or @fractos or @alanmackenzie).

Follow this [guide](https://support.cloudbees.com/hc/en-us/articles/203802500-Injecting-Secrets-into-Jenkins-Build-Jobs) to add credentials to the Global domain.
> E.g.
> - add ssh key with id `git`
> - add aws key pair as "AWS Credentials" kind with id `jenkins_aws`
