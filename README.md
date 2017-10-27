# Rancher Deploy


A command line application to deploy docker application to Rancher. 
RancherDeploy aims to keep its interface as similar as possible to
the docker CLI's in order to provide an intuitive user experience.
The main purpose of this script is to make it easier 
to enable continuous delivery and pairs nicely with Jenkins and Bamboo.
Currently, this app can create and remove stacks, services, and load
balancers. If a stack or service doesn't exist it will create one.
The app also has the ability to upgrade existing services.

RancherDeploy also ships with a python wrapper for the Rancher API
that you can use to create your own tools and utilities.

## Installation

### PIP

RanchdeDeploy is available in pypi and can be installed 
using pip : 

``` pip install rancherdelpoy  ```

### Docker

To build the Docker image :

``` docker build -t rancherdeploy .  ```

Once the image is build, bash into the container with:

``` docker run -it rancherdeploy bash ```

Once inside the container, RancherDeploy should be available as a CLI.

## Usage for CLI

``` RancherDeploy [OPTIONS] COMMAND [ARGS]...  ```


### Options

| Option | Description                |
|--------+----------------------------|
| --help | Show this message and exit |

### Commands

| Command       | Description                       |
|---------------+-----------------------------------|
| deploy        | Deploy a service/stack to rancher |
| setuplb       | Deploy a Load Balancer            |
| deletestack   | Delete an entire stack            |
| deleteservice | Delete a service                  |


### ARGS

For the deploy command

| ARG                  | Description                                          | Required |
|----------------------+------------------------------------------------------+----------|
| -u, --username       | Rancher API Username                                 | Yes      |
| --password           | Rancher API Password                                 | Yes      |
| -h, --host           | Rancher Server URL                                   | Yes      |
| --api_version        | Rancher API version                                  | Yes      |
| --rservice           | Rancher Service name                                 | Yes      |
| --rstack             | Rancher Stack name                                   | Yes      |
| -l, --label          | set meta data on a container                         | No       |
| -p, --publish        | Publish a container’s port(s) to the host            | No       |
| --image              | image name                                           | yes      |
| -e, --env            | Set environment variables                            | No       |
| --healthcheck_port   | Internal container port to health check              | No       |
| --healthcheck_method | GET/PUT/POST/HEAD etc. method to use for healthcheck | No       |
| --healthcheck_path   | HTTP parth for health check                          | No       |
| --memory             | Container level memory lock                          | No       |
| --memory_reservation | Used by Rancher for scheduling                       | No       |

Example:

```
RancherDeploy deploy \
-u $RANCHER_USER \
--password $RANCHER_PASS \
-h RANCHER_HOST \
--api_version v2-beta \
--rstack MY-STACK \
--rservice myservice \
-e evar1=VALUE \
-l label1=val1 \
--image docker:myservice:latest
```

For the setuplb command

| ARG              | Description                                                  | Required |
|------------------+--------------------------------------------------------------+----------|
| -u, --username   | Rancher API Username                                         | Yes      |
| --password       | Rancher API Password                                         | Yes      |
| -h, --host       | Rancher Server URL                                           | Yes      |
| --api_version    | Rancher API version                                          | Yes      |
| --rservice       | Rancher Service name of service to be load balanced          | Yes      |
| --rstack         | Rancher Stack name                                           | Yes      |
| -l, --label      | set meta data on a container                                 | No       |
| --lb_source_port | Port being exposed by the LB                                 | Yes      |
| --lb_target_port | Port inside the container of the service being load balanced | Yes      |

Example :

```
RancherDeploy setuplb \
-u $RANCHER_USER \
--password $RANCHER_PASS \
-h $RANCHER_HOST \
--api_version v2-beta \
--rstack MY-STACK \
--rservice myservice  \
--lb_source_port 9833 \
--lb_target_port 8080 \
```


for the deletestack command

| ARG              | Description                                                  | Required |
|------------------+--------------------------------------------------------------+----------|
| -u, --username   | Rancher API Username                                         | Yes      |
| --password       | Rancher API Password                                         | Yes      |
| -h, --host       | Rancher Server URL                                           | Yes      |
| --api_version    | Rancher API version                                          | Yes      |
| --rstack         | Rancher Stack name                                           | Yes      |

for the deleteservice commnad 

| ARG              | Description                                                  | Required |
|------------------+--------------------------------------------------------------+----------|
| -u, --username   | Rancher API Username                                         | Yes      |
| --password       | Rancher API Password                                         | Yes      |
| -h, --host       | Rancher Server URL                                           | Yes      |
| --api_version    | Rancher API version                                          | Yes      |
| --rservice       | Rancher Service name of service to be load balanced          | Yes      |
| --rstack         | Rancher Stack name                                           | Yes      |


## Usage for RancherDeploy library

As mentioned above, RancherDeploy ships with a wrapper for the rancher 
API that can be used to create custom scripts. This is the same 
library used to create the CLI and can do a all of the same functions 
including listing stacks and services, deleting stacks and services,
creating/upgrading stacks, services and load balancers. The example 
below demonstrates some of these functionalities.

```
>>> from RancherDeploy.Rancher import Rancher
>>> rancher = Rancher(url, (user,passw), v)
>>> rancher.stacks # List stacks
[healthcheck, network-services, ipsec, scheduler, Test1, Test2]
>>> rancher.stacks[-1].services # List services
[Hello1, Hello2]
>>> rancher.stacks[-1].services[0].status # Check status of services
'active'
>>> rancher.stacks[-1].services[0].remove() # Delete services
>>> rancher.stacks[-1].services
[Hello2]
>>> rancher.stacks[-1].remove() # Delete stacks
>>> rancher.stacks
[healthcheck, network-services, ipsec, scheduler, Test1]
>>>
```

## Troubleshooting


This script was developed against the v2-beta api and Rancher
V1.6.2. No other versions were tested.  If any error occur, verify the
version of Rancher and the API.

## How to contribute

If you notice a bug or would like to add improvements, please send a pull request with your fix.

## License 

Copyright 2017 Deluxe Corporation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
