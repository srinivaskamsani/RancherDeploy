import requests as r

class Service:

    def __init__(self, service_url, auth):
        self.service_url = service_url
        self.rancher_auth = auth
        self.name = None
        self.image_name = None
        self.scale = None
        self.props = None
        self.initilize()

    def initilize(self):
        if self.service_url:
            self.props = r.get(self.service_url, auth=self.rancher_auth).json()
            self.name = self.props['name']
            self.image_name = self.props['launchConfig']['imageUuid']
            self.scale = self.props['scale']
        

    def get_image_uuid(self):
        if not self.image_name.startswith('docker:'):
            self.image_name = "docker:" + self.image_name
            return self.image_name
        return self.image_name
    
    def update_launch_config(self):
        launch_config = { 'imageUuid': self.get_image_uuid(),
                          'instanceTriggeredStop': 'stop',
                          'startOnCreate' : True,
                          'tty' : True}

        return launch_config

    def update_service_request(self):
        lc = self.update_launch_config()
        return {'name' : self.name,
                'scale': self.scale,
                'launchConfig': lc,
                'secondaryLaunchConfigs': [],
                'publicEndpoints': [],
                'assignServiceIpAddress': False,
                'startOnCreate': True}
    
    def __repr__(self):
        return self.name
        
