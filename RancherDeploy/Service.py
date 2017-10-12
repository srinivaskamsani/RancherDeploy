import requests as r
from RancherDeploy.LoadBalancer import LoadBalancer
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
        self.ports = []
        self.env_vars = {}
        self.labels = {}
        self.healthcheck = None
        self.network_mode = 'managed'
        self.log_driver = ''
        self.initilize()


    @property
    def props(self):
        return r.get(self.service_url, auth=self.rancher_auth).json()
    
    def initilize(self):
        if self.service_url:
            cached_props = self.props 
            self.name = cached_props['name']
            self.id = cached_props['id']
            self.stack_id = cached_props['stackId']
            self.image_name = cached_props['launchConfig']['imageUuid']
            self.scale = cached_props['scale']
            self.ports = cached_props['launchConfig'].get('ports',[])
            self.network_mode = cached_props['launchConfig']['networkMode']
            self.env_vars = cached_props['launchConfig'].get('environment', {})
            self.labels = cached_props['launchConfig'].get('labels', {})

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
                          'healthCheck' : self.healthcheck,
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

    def finish_upgrade(self):
        finish_upgrade_url = self.props['actions']['finishupgrade']
        resp = r.post(finish_upgrade_url, auth=self.rancher_auth)

        if resp.status_code is not 202:
            raise ValueError("Could not finish upgrade", resp.json())
    
    def upgrade(self):
        upgrade_url = self.props['actions']['upgrade']
        lc = self.update_launch_config()
        payload = json.dumps({"inServiceStrategy": {"launchConfig": lc, "scale": self.scale}, "toServiceStrategy": None})
        resp = r.post(upgrade_url, data=payload, auth=self.rancher_auth)

        if resp.status_code is not 202:
            raise ValueError("upgrade failed", resp.json())

        while self.status != 'upgraded':
            pass

        self.finish_upgrade()
        
    def create_load_balancer(self, source_port, target_port, labels={}):
        '''
        source port is the port exposed by the load balancer
        target port is the port inside the container of service being 
        load balanced
        '''
        lb = LoadBalancer(None, self.rancher_auth)
        lb.name = self.name + "-LB"
        lb.service_id = self.id
        lb.stack_id = self.stack_id
        lb.source_port = source_port
        lb.target_port = target_port
        lb.labels = labels
        create_new_request = lb.update_lb_request()

        services_link = r.get(self.props['links']['stack'], auth=self.rancher_auth).json()['links']['services']
        create_lb_link = r.get(services_link, auth=self.rancher_auth).json()['createTypes']['loadBalancerService']

        resp = r.post(create_lb_link, auth=self.rancher_auth, json=create_new_request)

        if resp.status_code != 201:
            raise ValueError("Could not create LB :", resp.json())

    def remove(self):
        remove_url = self.props['actions']['remove']
        resp = r.post(remove_url, auth=self.rancher_auth)

        if resp.status_code != 202:
            raise ValueError("Removing Service failed:", resp.json())

    def add_healthcheck(self, port, method, path):

        request_line = method.upper() + " " + '"' + path + '"' + " " + '"HTTP/1.0"'
        self.healthcheck =  { "type": "instanceHealthCheck",
                              "healthyThreshold": 2,
                              "initializingTimeout": 60000,
                              "interval": 2000,
                              "name": None,
                              "port": port,
                              "reinitializingTimeout": 60000,
                              "requestLine": request_line,
                              "responseTimeout": 2000,
                              "strategy": "recreate",
                              "unhealthyThreshold": 3} 
        
    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other
        
