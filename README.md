# Rancher Deploy


A command line application to deploy docker application to Rancher. A stack will be created if one doesn't exist. A new services will created if one doesn't exist. If a service exists, the script will upgrade that service with it's new configurations.

## Installation

### PIP

From the root directory, do

```
pip install .
```

### Docker

To build the Docker image :

```
docker build -t rancherdeploy .
```

Once the image is build, bash into the container with:

```
docker run -it rancherdeploy bash
```

Once inside the container, RancherDeploy should be available as a CLI.

## Usage

```
RancherDeploy [OPTIONS] COMMAND [ARGS]...
```


### Options

| Option | Description                |
|--------+----------------------------|
| --help | Show this message and exit |

### Commands

| Command | Description                       |
|---------+-----------------------------------|
| deploy  | Deploy a service/stack to rancher |


### ARGS

| ARG            | Description                               | Required |
|----------------+-------------------------------------------+----------|
| -u, --username | Rancher API Username                      | Yes      |
| --password     | Rancher API Password                      | Yes      |
| -p, --publish  | Publish a container’s port(s) to the host | No       |
| -h, --host     | Rancher Server URL                        | Yes      |
| --api_version  | Rancher API version                       | Yes      |
| --rstack       | Rancher Stack name                        | Yes      |
| --rservice     | Rancher Service name                      | Yes      |
| --image        | image name                                | yes      |
| -e, --env      | Set environment variables                 | No       |
| -l, --label    | set meta data on a container              | No       |


## Troubleshooting


This script was developed against the v2-beta api and Rancher V1.6.2. No other versions were tested.
If any error occur, verify the version of Rancher and the API. 

Usual errors related to network issues could occur.
