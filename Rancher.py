import requests as r
from  Stack import Stack
from urllib.parse import urljoin

class Rancher:
    def __init__(self, rancher_url, rancher_auth, api_verison):
        self.rancher_url = rancher_url
        self.rancher_auth = rancher_auth
        self.api_verison = api_verison
        self.api_endpoint = urljoin(self.rancher_url, self.api_verison)

    @property
    def stacks(self):
        rancher_props = r.get(self.api_endpoint, auth=self.rancher_auth).json()
        stacks_url = rancher_props['links']['stacks']
        stacks = r.get(stacks_url, auth=self.rancher_auth).json()['data']

        stacks_accum = []
        for stack in stacks:
            s = Stack(stack['links']['self'], self.rancher_auth)
            stacks_accum.append(s)
        return stacks_accum

    def create_new_stack(self, stack_name):
        rancher_props = r.get(self.api_endpoint, auth=self.rancher_auth).json()
        stacks_url = rancher_props['links']['stacks']
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
        

    
