import requests as r
from RancherDeploy.Service import Service
import json
from RancherDeploy.LoadBalancer import LoadBalancer
class Stack:
    def __init__(self, stack_url, auth):
        self.stack_url = stack_url
        self.rancher_auth = auth
        self.props = r.get(self.stack_url, auth=self.rancher_auth).json()

    @property
    def name(self):
        return self.props['name']

    @property
    def services(self):
        services_url = self.props['links']['services']
        services_prop = r.get(services_url, auth=self.rancher_auth).json()
        services = services_prop['data']

        services_accum =[]
        for service in services:
            if service['type'] == 'service':
                s = Service(service['links']['self'], self.rancher_auth)
                services_accum.append(s)
            elif service['type'] == 'loadBalancerService':
                s = LoadBalancer(service['links']['self'], self.rancher_auth)
                services_accum.append(s)
                

        return services_accum

    def create_new_service(self, service):
        services_url = self.props['links']['services']
        services_prop = r.get(services_url, auth=self.rancher_auth).json()
        create_service_url = services_prop['createTypes']['service']
        payload = service.update_service_request()
        payload['stackId'] = self.props['id']
        payload['scalePolicy'] = ""
        payload['lbConfig'] = ""
        resp = r.post(create_service_url, data=json.dumps(payload), auth=self.rancher_auth)

        if resp.status_code != 201:
            raise ValueError("Creatnig a new service failed:", resp.json())

        return Service(resp.json()['links']['self'], self.rancher_auth)

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other
        