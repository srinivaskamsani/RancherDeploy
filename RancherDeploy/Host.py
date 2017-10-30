'''
This module contains all operations
related to Hosts in Rancher
'''

import logging
import requests as r


class Host:
    '''
    Class models Hosts in Rancher
    '''

    def __init__(self, host_url, auth):
        self.host_url = host_url
        self.rancher_auth = auth
        self.hostname = None
        self.initilize()

    def initilize(self):
        '''
        Cache relevent values obtained from calling the
        host endpoint of the rancher API.
        '''
        host_props = r.get(self.host_url, auth=self.rancher_auth).json()
        if self.host_url:
            self.hostname = host_props['hostname']

    def evacuate(self):
        '''
        Call the evacuate action on the current host
        '''
        host_props = r.get(self.host_url, auth=self.rancher_auth).json()
        evacuate_url = host_props['actions']['evacuate']
        resp = r.post(evacuate_url, auth=self.rancher_auth)
        return resp

    def deactivate(self):
        '''
        Deactivate the current host
        '''
        host_props = r.get(self.host_url, auth=self.rancher_auth).json()
        deactivate_url = host_props['actions']['deactivate']
        resp = r.post(deactivate_url, auth=self.rancher_auth)
        return resp

    def activate(self):
        '''
        Activate the current host
        '''
        self_props = r.get(self.host_url, auth=self.rancher_auth).json()
        activate_url = self_props['actions'].get('activate')
        if not activate_url:
            logging.info("Action unavailable: activate")
            return

        resp = r.post(activate_url, auth=self.rancher_auth)
        return resp

    def remove(self):
        '''
        Remove the current host from Rancher
        '''
        host_props = r.get(self.host_url, auth=self.rancher_auth).json()
        remove_url = host_props['actions'].get('remove')
        if not remove_url:
            logging.info("Action unavailable: remove")
            return

        resp = r.post(remove_url, auth=self.rancher_auth)
        return resp

    def __repr__(self):
        return self.hostname
