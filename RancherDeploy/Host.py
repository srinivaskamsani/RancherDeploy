import requests as r
from urllib.parse import urljoin
import logging

class Host:
    def __init__(self, host_url, auth):
        self.host_url = host_url
        self.rancher_auth = auth
        self.hostname = None
        self.initilize()

    def initilize(self):
        host_props = r.get(self.host_url, auth=self.rancher_auth).json()
        if self.host_url:
            self.hostname = host_props['hostname']

    def evacuate(self):
        host_props = r.get(self.host_url, auth=self.rancher_auth).json()
        evacuate_url = host_props['actions']['evacuate']
        resp = r.post(evacuate_url, auth=self.rancher_auth)
        return resp

    def deactivate(self):
        host_props = r.get(self.host_url, auth=self.rancher_auth).json()
        deactivate_url = host_props['actions']['deactivate']
        resp = r.post(deactivate_url, auth=self.rancher_auth)
        return resp

    def activate(host):
        self_props = r.get(self.host_url, auth=self.rancher_auth).json()
        activate_url = host_props['actions'].get('activate')
        if not activate_url:
            logging.info("Action unavailable: activate")
            return
        
        resp = r.post(activate_url, auth=self.rancher_auth)
        return resp

    def remove(self):
        host_props = r.get(self.host_url, auth=self.rancher_auth).json()
        remove_url = host_props['actions'].get('remove')
        if not remove_url:
            logging.info("Action unavailable: remove")
            return
        
        resp = r.post(remove_url, auth=self.rancher_auth)
        return resp
    
    def __repr__(self):
        return self.hostname
    
        
    
