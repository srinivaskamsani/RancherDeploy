import requests as r
from LoadBalancer import LoadBalancer
import json

class Service:

    def __init__(self, service_url, auth):
        self.service_url = service_url
        self.rancher_auth = auth
        self.name = None
        self.id = None
        self.stack_id = None
        self.image_name = None
        self.scale = None
        self.props = None
        self.ports = []
        self.env_vars = {}
        self.labels = {}
        self.network_mode = 'managed'
        self.log_driver = ''
        self.initilize()

    def initilize(self):
        if self.service_url:
            self.props = r.get(self.service_url, auth=self.rancher_auth).json()
            self.name = self.props['name']
            self.id = self.props['id']
            self.stack_id = self.props['stackId']
            self.image_name = self.props['launchConfig']['imageUuid']
            self.scale = self.props['scale']
            self.ports = self.props['launchConfig']['ports']
            self.network_mode = self.props['launchConfig']['networkMode']
            self.env_vars = self.props['launchConfig'].get('environment', {})
            self.labels = self.props['launchConfig']['labels']

    @property
    def status(self):
        props = r.get(self.service_url, auth=self.rancher_auth).json()
        return props['state']
    
    def expose_port(self, internal, external=None):
        if not ("/tcp" in internal or "/udp" in internal):
            internal = internal + "/tcp"

        if external:
            self.ports.append(external + ":" + internal)
        else:
            self.ports.append(internal)

    def add_env_var(self, key,value):
        self.env_vars.update({key : value})            

    def add_label(self, key, value):
        self.labels.update({key : value})
        
    def get_image_uuid(self):
        if not self.image_name.startswith('docker:'):
            self.image_name = "docker:" + self.image_name
            return self.image_name
        return self.image_name

    def update_log_config(self):
        log_config = {'type': 'logConfig',
                      'config': {},
                      'driver': self.log_driver}
        return log_config
    
    def update_launch_config(self):
        launch_config = { 'imageUuid': self.get_image_uuid(),
                          'instanceTriggeredStop': 'stop',
                          'startOnCreate' : True,
                          'tty' : True,
                          'ports': self.ports,
                          'networkMode': self.network_mode,
                          'environment': self.env_vars,
                          'labels': self.labels,
                          'logConfig': self.update_log_config() }

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
    @property
    def upgrade_url(self):
        props = r.get(self.service_url, auth=self.rancher_auth).json()
        return props['actions']['upgrade']
    
    def upgrade(self):
        lc = self.update_launch_config()
        payload = json.dumps({"inServiceStrategy": {"launchConfig": lc, "scale": self.scale}, "toServiceStrategy": None})
        resp = r.post(self.upgrade_url, data=payload, auth=self.rancher_auth)

        if resp.status_code is not 202:
            raise ValueError("upgrade failed", resp.json())

        while self.status != 'upgraded':
            pass
        
    def create_load_balancer(self, internal_port, external_port):
        lb = LoadBalancer(self.rancher_auth)
        lb.name = self.name + "LB"
        lb.service_id = self.id
        lb.stack_id = self.stack_id
        lb.service_port = internal_port
        lb.lb_ports = ["9213:9213/tcp"]

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other
        
