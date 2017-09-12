import requests as r

class LoadBalancer:
    def __init__(self, lb_url, auth):
        self.lb_url = lb_url
        self.rancher_auth = auth
        self.image_name = 'docker:rancher/lb-service-haproxy:v0.7.5'
        self.name = ''
        self.lb_ports = []
        self.props = None
        self.service_id = None
        self.stack_id = None
        self.source_port = None
        self.target_port = None
        self.labels = {}
        self.name = None
        self.initilize()
        
    def initilize(self):
        if self.lb_url:
            self.props = r.get(self.lb_url, auth=self.rancher_auth).json()
            self.image_name = self.props['launchConfig']['imageUuid']
            self.labels = self.props['launchConfig']['labels']
            self.name = self.props['name']
            self.lb_ports = self.props['launchConfig']['ports']
            self.source_port = self.props['lbConfig']['portRules'][0]['sourcePort']
            self.target_port = self.props['lbConfig']['portRules'][0]['targetPort']
            self.service_id  = self.props['lbConfig']['portRules'][0]['serviceId']
            self.stack_id = self.props['stackId']
            
    def __repr__(self):
        return self.name

    def update_launch_config_request(self):
        port = str(self.source_port) + ":" + str(self.source_port) + "/tcp"
        return {'imageUuid' : 'docker:rancher/lb-service-haproxy:v0.7.5',
                'ports' : [port],
                'labels': self.labels,
                'startOnCreate' : True}

    def update_lb_config_request(self):
        return {'portRules': [{'path': '',
                               'priority': 1,
                               'protocol': 'http',
                               'serviceId': self.service_id,
                               'sourcePort': self.source_port,
                               'targetPort': self.target_port,
                               'type': 'portRule'}]}
    
    def update_lb_request(self):
        return {'launchConfig' : self.update_launch_config_request(),
                'lbConfig': self.update_lb_config_request(),
                'name': self.name,
                'scale': 1,
                'scalePolicy' : '',
                'stackId': self.stack_id,
                'startOnCreate': True}

    def remove(self):
        remove_url = self.props['actions']['remove']
        resp = r.post(remove_url, auth=self.rancher_auth)
        if resp.status_code != 202:
            raise ValueError("Unable to remove load balancer", resp.json())
        
    def __eq__(self, other):
        return self.name == other
