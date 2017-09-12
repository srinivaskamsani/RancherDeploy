# Rancher Deploy


A command line application to deploy docker application to Rancher. A
stack will be created if one doesn't exist. A new services will
created if one doesn't exist. If a service exists, the script will
upgrade that service with it's new configurations. The app also has the 
ability to deploy load balances.

## Installation

### PIP

From the root directory, do

``` pip install .  ```

### Docker

To build the Docker image :

``` docker build -t rancherdeploy .  ```

Once the image is build, bash into the container with:

``` docker run -it rancherdeploy bash ```

Once inside the container, RancherDeploy should be available as a CLI.

## Usage

``` RancherDeploy [OPTIONS] COMMAND [ARGS]...  ```


### Options

| Option | Description                |
|--------+----------------------------|
| --help | Show this message and exit |

### Commands

| Command | Description                       |
|---------+-----------------------------------|
| deploy  | Deploy a service/stack to rancher |
| setuplb | Deploy a Load Balancer            |


### ARGS

For the deploy command

| ARG            | Description                               | Required |
|----------------+-------------------------------------------+----------|
| -u, --username | Rancher API Username                      | Yes      |
| --password     | Rancher API Password                      | Yes      |
| -h, --host     | Rancher Server URL                        | Yes      |
| --api_version  | Rancher API version                       | Yes      |
| --rservice     | Rancher Service name                      | Yes      |
| --rstack       | Rancher Stack name                        | Yes      |
| -l, --label    | set meta data on a container              | No       |
| -p, --publish  | Publish a container’s port(s) to the host | No       |
| --image        | image name                                | yes      |
| -e, --env      | Set environment variables                 | No       |

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

## Troubleshooting


This script was developed against the v2-beta api and Rancher
V1.6.2. No other versions were tested.  If any error occur, verify the
version of Rancher and the API.

Usual errors related to network issues could occur.
