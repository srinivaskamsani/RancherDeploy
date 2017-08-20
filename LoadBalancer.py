import requests as r

class LoadBalancer:
    def __init__(self, auth, lb_url=None):
        self.lb_url = lb_url
        self.rancher_auth = auth
        self.image_name = 'docker:rancher/lb-service-haproxy:v0.7.5'
        self.name = ''
        self.lb_ports = []
        self.props = None
        self.service_id = None
        self.stack_id = None
        self.service_port = None
        self.initilize()
        
    def initilize(self):
        if self.lb_url:
            self.props = r.get(self.lb_url, auth=self.rancher_auth).json()
            self.image_name = self.props['launchConfig']['imageUuid']
            self.name = self.props['name']
            self.lb_ports = self.props['launchConfig']['ports']

    def __repr__(self):
        return self.name

    def update_lb_request(self):
        pass
        
            
            
