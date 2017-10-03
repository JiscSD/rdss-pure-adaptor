# RDSS Pure Adaptor
> E.g. rdss-default-service-ac

## { Service Name }

### Description
> This section should describe what the new service is.

### Language / Framework
> E.g.
> - Python 3.6+
> - Flask

### Service Infrastructure

 > E.g. Supported environments
 > - dev
 > - uat
 > - prod

#### Sub-Services
> E.g.
> - AWS Lambda
> - AWS RDS


---------------------------------------------------------

## Deployment

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
