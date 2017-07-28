import requests as r

class LoadBalancer:
    def __init__(self, lb_url, auth):
        self.lb_url = lb_url
        self.rancher_auth = auth
        self.image_name = None
        self.name = ''
        self.lb_ports = []
        self.props = r.get(self.lb_url, auth=self.rancher_auth).json()
        self.initilize()
        
    def initilize(self):
        if lb_url:
            self.image_name = self.props['launchConfig']['imageUuid']
            self.name = self.props['name']
            self.lb_ports = self.props['launchConfig']['ports']
            
            
