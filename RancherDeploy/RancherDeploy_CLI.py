import click
from RancherDeploy.Rancher import Rancher
from collections import namedtuple
import logging
import re
from RancherDeploy.Service import Service
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help', ''])

def get_item_from_list(item, lst):
    for l in lst:
        if item == l:
            return l
    return None
        
def convert_tuple_to_dict(variables):
    '''
    From: ('key1'='val1', 'key2'='val2')
    To  : {'key1:val1', 'key2:val2'}
    '''
    return {k:v for (k, v) in [tuple(var.split('=',1)) for var in variables]}

def convert(dictionary):
    '''
    https://gist.github.com/href/1319371
    '''
    return namedtuple('GenericDict', dictionary.keys())(**dictionary)

def convert_ports(ports):
    '''
    From: ('8080:9090', '9090')
    To  : ['8080:9090/tcp', '9090/tcp']
    '''
    return [re.sub('([0-9])$', '\g<1>/tcp', p) for p in ports]

@click.group()
def main():
    pass

@main.command()
@click.option('-u', '--username', help='Rancher API Username', required=True)
@click.option('--password', help='Rancher API Password', required=True)
@click.option('-p','--publish' , help='Publish a container’s port(s) to the host', required=False, multiple=True)
@click.option('-h', '--host', help='Rancher Server URL', required=True)
@click.option('--api_version', help='Rancher API version', required=True)
@click.option('--rstack', help='Rancher Stack name', required=True)
@click.option('--rservice', help='Rancher Service name', required=True)
@click.option('--image', help='image name', required=True)
@click.option('-e', '--env', help='Set environment variables', required=False, multiple=True)
@click.option('-l', '-label', help='Set meta data on a container', required=False, multiple=True)
@click.option('--healthcheck_port', help='Internal container port to health check', required=False)
@click.option('--healthcheck_method', help='GET/PUT/POST/HEAD etc. method to use for healthcheck', required=False)
@click.option('--healthcheck_path', help='HTTP path for health check', required=False)
def deploy(**kwargs):
    configs = convert(kwargs)
    rancher_auth = (configs.username,configs.password)
    rancher = Rancher(configs.host, rancher_auth, configs.api_version)

    if configs.rstack not in rancher.stacks:
        logging.info("Creating new stack for %s", configs.rstack)
        rancher.create_new_stack(configs.rstack)

    stack = get_item_from_list(configs.rstack, rancher.stacks)
    
    s = Service(None, rancher_auth)
    s.name = configs.rservice
    s.image_name = configs.image
    s.scale = 1
    s.env_vars = convert_tuple_to_dict(configs.env)
    s.labels = convert_tuple_to_dict(configs.label)
    s.ports = convert_ports(configs.publish)

    if all([configs.healthcheck_port, configs.healthcheck_method,
                      configs.healthcheck_path]):
        
        s.add_healthcheck(configs.healthcheck_port, configs.healthcheck_method,
                          configs.healthcheck_path)
    if configs.rservice not in stack.services:
        new_service = stack.create_new_service(s)
    else:
        target_service = get_item_from_list(configs.rservice, stack.services)
        s.service_url = target_service.service_url
        s.upgrade()

@main.command()
@click.option('-u', '--username', help='Rancher API Username', required=True)
@click.option('--password', help='Rancher API Password', required=True)
@click.option('-h', '--host', help='Rancher Server URL', required=True)
@click.option('--api_version', help='Rancher API version', required=True)
@click.option('--rstack', help='Rancher Stack name', required=True)
@click.option('--rservice', help='Rancher Service name of service to be load balanced', required=True)
@click.option('--lb_source_port', help='Port being exposed by the LB', required=True)
@click.option('--lb_target_port', help=' port inside the container of service being load balanced', required=True)
@click.option('-l', '-label', help='Set meta data on a container', required=False, multiple=True)
def SetUpLB(**kwargs):
    configs = convert(kwargs)
    rancher_auth = (configs.username,configs.password)
    rancher = Rancher(configs.host, rancher_auth, configs.api_version)
    lb_name = configs.rservice + "-LB"
    if configs.rstack not in rancher.stacks:
        raise ValueError("Stack does not exit. Please create it first")

    stack = get_item_from_list(configs.rstack, rancher.stacks)
    services = stack.services
    if configs.rservice not in services:
        raise ValueError("Can't create a LB for a service does not exist. Please check.")

    if lb_name in services:
        target_lb = get_item_from_list(lb_name, services)
        target_lb.remove()
        
    target_service = get_item_from_list(configs.rservice, services)
    target_service.create_load_balancer(configs.lb_source_port, configs.lb_target_port, convert_tuple_to_dict(configs.label))

@main.command()
@click.option('-u', '--username', help='Rancher API Username', required=True)
@click.option('--password', help='Rancher API Password', required=True)
@click.option('-h', '--host', help='Rancher Server URL', required=True)
@click.option('--api_version', help='Rancher API version', required=True)
@click.option('--rstack', help='Rancher Stack name', required=True)
def deletestack(**kwargs):
    configs = convert(kwargs)
    rancher_auth = (configs.username, configs.password)
    rancher = Rancher(configs.host, rancher_auth, configs.api_version)

    target_stack = get_item_from_list(configs.rstack, rancher.stacks)
    target_stack.remove()

@main.command()
@click.option('-u', '--username', help='Rancher API Username', required=True)
@click.option('--password', help='Rancher API Password', required=True)
@click.option('-h', '--host', help='Rancher Server URL', required=True)
@click.option('--api_version', help='Rancher API version', required=True)
@click.option('--rstack', help='Rancher Stack name', required=True)
@click.option('--rservice', help='Rancher Service name of service to be load balanced', required=True)
def deletestack(**kwargs):
    configs = convert(kwargs)
    rancher_auth = (configs.username, configs.password)
    rancher = Rancher(configs.host, rancher_auth, configs.api_version)

    target_stack = get_item_from_list(configs.rstack, rancher.stacks)
    target_service = get_item_from_list(configs.rstack, target_stack.services)
    target_service.remove()
    
if __name__ == '__main__':
    main()
