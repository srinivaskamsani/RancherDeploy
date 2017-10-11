import requests as r
from  RancherDeploy.Stack import Stack
from RancherDeploy.Host import Host
from urllib.parse import urljoin
import logging
import sys

class Rancher:
    def __init__(self, rancher_url, rancher_auth, api_verison):
        self.rancher_url = rancher_url
        self.rancher_auth = rancher_auth
        self.api_verison = api_verison
        self.api_endpoint = urljoin(self.rancher_url, self.api_verison)
        self.rancher_props = r.get(self.api_endpoint, auth=self.rancher_auth).json()

    @property
    def stacks(self):
        projects_url = self.rancher_props['links']['projects']
        projects = r.get(projects_url, auth=self.rancher_auth).json()
        stacks_url = projects['data'][0]['links']['stacks']
        stacks = r.get(stacks_url, auth=self.rancher_auth).json()['data']

        stacks_accum = []
        for stack in stacks:
            s = Stack(stack['links']['self'], self.rancher_auth)
            stacks_accum.append(s)
        return stacks_accum

    @property
    def hosts(self):
        host_url = self.rancher_props['links']['hosts']
        hosts = r.get(host_url, auth=self.rancher_auth).json()['data']

        hosts_accum = []
        for host in hosts:
            h = Host(host['links']['self'], self.rancher_auth)
            hosts_accum.append(h)

        return hosts_accum
            
        
    def create_new_stack(self, stack_name):
        projects_url = self.rancher_props['links']['projects']
        projects = r.get(projects_url, auth=self.rancher_auth).json()
        stacks_url = projects['data'][0]['links']['stacks']
        stacks = r.get(stacks_url, auth=self.rancher_auth).json()
        create_endpoint = stacks['createTypes']['stack']
        new_stack_request = self.__new_stack_request(stack_name)
        resp = r.post(create_endpoint, data=new_stack_request, auth=self.rancher_auth)
        if resp.status_code != 201:
            logging.fatal("Unable to create stack: %s", resp.text)
            sys.exit(1)
        

    def __new_stack_request(self, stack_name):
        return {"name": stack_name,
                "system": False,
                "dockerCompose":"",
                "rancherCompose":""}
        

    
