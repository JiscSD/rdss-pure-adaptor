# RDSS Pure Adaptor

A per-institution adaptor for installations of the [Pure research information system](https://www.elsevier.com/solutions/pure). This adaptor periodically polls the `datasets` endpoint of a Pure installation, fetching new and modified datasets, and relaying these datasets on to the Jisc Research Data Shared Service (RDSS). At present the RDSS Pure Adaptor can interact with version 5.9 of the Pure API, but is designed to easily accommodate interaction with other versions of the API in future.  

### Language / Framework

- Python 3.6+

### Service Infrastructure

#### Supported Environments

The following environments are supported on an institution by institution basis:

- dev
- uat
- prod

#### Sub-Services

The RDSS Pure Adaptor depends on the following infrastructure:

- AWS Kinesis Streams
- AWS DynamoDB
- AWS S3 Buckets

## Configuration

The RDSS Pure Adaptor requires that the following environment variables are set:

- `PURE_API_VERSION`

   A string description of the Pure API version being targeted. Used to select the Pure API integration used by the RDSS Pure Adaptor.

- `PURE_API_URL`

   The url of the Pure API endpoint.

- `PURE_API_KEY`

   The api key which is used to authorise access to the Pure API endpoint.

- `INSTANCE_ID`

   A string describing the institution and environment which this instance of the RDSS Pure Adaptor is targeting, e.g. `pure-adaptor-<jisc_id>-<env>`. This is the name of the DynamoDB table used to store the state of the adaptor, as well as the name of the s3 bucket which the adaptor will upload downloaded datasets.

- `RDSS_INTERNAL_INPUT_STREAM`

   The name of the RDSS internal input stream to which the Pure Adaptor will write messages.

- `RDSS_MESSAGE_INVALID_STREAM`

   The name of the RDSS invalid message stream to which the Pure Adaptor will write invalid messages.

- `RDSS_MESSAGE_ERROR_STREAM`

   The name of the RDSS error message stream to which the Pure Adaptor will write error messages.

In addition to the aforementioned variables, the following environment variables are also required by the `boto3` library to access the AWS resources utilised by the RDSS Pure Adaptor:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`


## Deployment

The RDSS Pure Adaptor is intended to be deployed as a service on a per-institution and per-environment basis as part of the RDSS institutional ECS clusters infrastructure. This repository is targeted by a build task defined in the [RDSS Institutional ECS Clusters](https://github.com/JiscRDSS/rdss-institutional-ecs-clusters) repository. This task will build the Docker image defined by the [Dockerfile](/Dockerfile) in this repository. The RDSS Pure Adaptor is provided as a generic docker image which is configured by the environmental variables outlined in the [Configuration](#configuration) section.


## Test

To run the test suite for the RDSS Pure Adaptor, run the following command:

```
make test
```


## Developer Setup

To run the adaptor locally, first all the required environment variables must be set, e.g.:
```
export PURE_API_VERSION=v59
...
```
Then to create a local virtual environment, install dependencies and manually run the adaptor:
```
make env
source ./env/bin/activate
make deps
python ./pure_adaptor/pure_adaptor.py
```
