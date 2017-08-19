# Rancher Deploy


A commandline application to deploy docker applcation to Rancher. A stack will be created if one doesn't exist. A new services will created if one doesn't exist. If a service exists, the script will upgrade that service with it's new configurations.


## Usage

```
RancherDeploy_CLI.py [OPTIONS] COMMAND [ARGS]...
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

