import click
from Rancher import Rancher
from collections import namedtuple
import logging
from Service import Service
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help', ''])

def convert_tuple_to_dict(variables):
    '''
    From: ('key1'='val1', 'key2'='val2')
    To  : {'key1:val1', 'key2:val2'}
    '''
    d = dict()
    if variables:
        for var in variables:
            k,v = var.split('=',1)
            d[k] = v
    return d

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
    l = list()
    if ports:
        for port in ports:
            if not ("/tcp" in port or "/udp" in port):
                l.append(port + "/tcp")
            else:
                l.append(port)
    return l

@click.group()
def cli():
    pass

@cli.command()
@click.option('-u', '--username', help='Rancher API Username', required=True)
@click.option('--password', help='Rancher API Password', required=True)
@click.option('-p','--publish' , help='Give extended privileges to this container', required=False, multiple=True)
@click.option('-h', '--host', help='Rancher Server URL', required=True)
@click.option('--api_version', help='Rancher API version', required=True)
@click.option('--rstack', help='Rancher Stack name', required=True)
@click.option('--rservice', help='Rancher Service name', required=True)
@click.option('--image', help='image name', required=True)
@click.option('-e', '--env', help='Set environment variables', required=False, multiple=True)
@click.option('-l', '-label', help='Set meta data on a container', required=False, multiple=True)
def deploy(**kwargs):
    configs = convert(kwargs)
    rancher_auth = (configs.username,configs.password)
    rancher = Rancher(configs.host, rancher_auth, configs.api_version)

    if configs.rstack not in rancher.stacks:
        logging.info("Creating new stack for %s", configs.rstack)
        rancher.create_new_stack(configs.rstack)

    stack = rancher.stacks[rancher.stacks.index(configs.rstack)] ## Arun Lazy. Change this.
    
    s = Service(None, rancher_auth)
    s.name = configs.rservice
    s.image_name = configs.image
    s.scale = 1
    s.env_vars = convert_tuple_to_dict(configs.env)
    s.labels = convert_tuple_to_dict(configs.label)
    s.ports = convert_ports(configs.publish)

    
    if configs.rservice not in stack.services:
        new_service = stack.create_new_service(s)
    else:
        target_service = stack.services[stack.services.index(configs.rservice)] ## Arun Lazy. Change this.
        s.service_url = target_service.service_url
        s.upgrade()
        
if __name__ == '__main__':
    cli()
