# RDSS Pure Adaptor

[![Build Status](https://travis-ci.com/JiscRDSS/rdss-pure-adaptor.svg?branch=master)](https://travis-ci.com/JiscRDSS/rdss-pure-adaptor)

## Contents

- [Introduction](#introduction)
- [Language / Framework](#language-framework)
- [Service Architecture](#service-architecture)
	- [API Calls](#api-calls)
	- [CRUD Capabilities](#crud-capabilities)
	- [Sub-Services](#sub-services)
	- [Metadata transformations](#metadata-transformations)
- [Configuration](#configuration)
    - [Adaptor poll frequency](#adaptor-poll-frequency)
- [Developer Setup](#developer-setup)
	- [Testing](#testing)
	- [Linting](#linting)
- [Frequently Asked Questions](#frequently-asked-questions)
	- [Is the adaptor multi tenanted?](#is-the-adaptor-multi-tenanted)
	- [What is the impact of polling?](#what-is-the-impact-of-polling)

## Introduction

The RDSS Pure Adaptor is a per-institution adaptor for installations of the [Pure research information system](https://www.elsevier.com/solutions/pure).

The adaptor periodically polls the `datasets/` endpoint of a Pure installation, fetching new and modified datasets, and relaying these datasets on to the Jisc Research Data Shared Service (RDSS).

At present the RDSS Pure Adaptor can interact with version 5.9 of the Pure API, but is designed to easily accommodate interaction with other versions of the API in future.  

## Language / Framework

- Python 3.6+
- Docker

## Service Architecture

The adaptor runs as a docker container which can be configured to poll the URL of institutions Pure instance API.

A checksum is created for each dataset and stored in DynamoDB to determine if a dataset has been added or modified since the last poll.

If a change is detected, the dataset is downloaded to S3 and the appropriate `Create` or `Update` message is published on the configured Kinesis Stream.

The below diagram illustrates how the adaptor functions:

![RDSS Pure Adaptor Diagram](docs/images/rdss-pure-adaptor.png)

### API Calls

The adaptor will make the following calls to the Pure endpoint:

| Action | Reason |
| ------ | ------ |
| `HTTP HEAD <PURE_API_URL>/datasets` | Ensure the endpoint is available. |
| `HTTP GET <PURE_API_URL>/datasets` | Retrieve a list of datasets. |
| `HTTP GET <PURE_API_URL>/datasets/<UUID>` | Retrieve a specific dataset |

### CRUD Capabilities

#### RDSS CRUD Actions

The adaptor currently supports the following actions with RDSS:

| Action | Reason |
| ------ | ------ |
| **READ** | Determine if a dataset has already been harvested. |
| **CREATE** | Create a new dataset that has been added to pure. |
| **UPDATE** | Update a dataset that has been modified in pure. |

#### PURE CRUD Actions

The adaptor currently supports with following actions with PURE:

| Action | Reason |
| ------ | ------ |
| **READ** | Retrieve datasets to be harvested. |

### Sub-Services

The RDSS Pure Adaptor depends on the following infrastructure:

- AWS Kinesis Streams
- AWS DynamoDB
- AWS S3 Buckets

### Metadata transformations

The Pure API sends messages that conform to a Pure schema. The adaptor converts these
messages to the CDM schema using JMESPath query language. The conversion expressions
are specified in `research_object_mapping.txt` file. Some conversions require mapping
lookups on the `taxonomyschema` repository. These are specified in the `JMESCustomFunctions`
class in `remapper.py`

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

- `JISC_ID`

   The JISC id of the HEI

- `HEI_ADDRESS`

   The address of the HEI

- `PURE_API_KEY_SSM_PARAMETER_NAME`

   The name of the AWS SSM parameter that contains the Pure API Key


In addition to the aforementioned variables, the following environment variables are also required by the `boto3` library to access the AWS resources utilised by the RDSS Pure Adaptor:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`


### Adaptor poll frequency

By default, the Pure adaptor polls the HEI Pure API endpoint every 60 minutes. However for testing or other purposes,
you may wish for the adaptor to poll the Pure endpoint more frequently. In this case, you need to set a value (in minutes) to the
environment variable `PURE_POLL_FREQUENCY` in the HEI specific configuration in the `rdss-institutional-ecs-clusters` repository.


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
python -m pure_adaptor.pure_adaptor
```

### Testing

To run the test suite for the RDSS Pure Adaptor, run the following command:

```
make test
```

In the dev environment, it is possible to have the adaptor process records it has already processed by removing them from the dynamodb table for the pure adaptor. In the AWS Console:
 - Navigate to the DynamoDB service then select the Tables view. 
 - Search for the table for the pure-adaptor that includes the Jisc ID for the HEI you are testing. 
 - Select that table to gain access to the items tab.
 - In the items tab, select some records that are recent.  These records will be still available in the Kinesis Stream.
 - Choose the 'Delete' action from the list of actions on the item tab page.

This should lead to the pure adaptor picking up records from the kinesis stream on its next scheduled run.

### Linting

To run the automated linting tool, run the following command:

```
make lint
```

## Frequently Asked Questions

### Is the adaptor multi tenanted?

No, the pure adaptor is designed to be run once for each specific institution.

The reason behind this decision is to allow flexibility to tailor metadata mappings for each institutions individual requirements.

### What is the impact of polling?

The pure adaptor is setup to poll the configured Pure endpoint once every 60 miniutes. As such, there may be up to a 60 miniute delay before new dataset create/update messages are published.
