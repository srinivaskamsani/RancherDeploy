#!/usr/bin/env python
import requests as r
import json
import sys
import ast
import os
import optparse


def evars_parser(evars):
    '''
    From: ['key1'='val1', 'key2'='val2']
    To  : ['key1:val1', 'key2:val2']
    '''
    d = dict()
    if evars:
        for var in evars:
            k, v = var.split('=', 1)
            d[k] = v
    return d


def ports_parser(ports):
    '''
    From: ['8080:9090', '9090'] 
    To  : ['8080:9090/tcp', '9090/tcp'] 
    '''
    l = list()

    if ports:
        for port in ports:
            l.append(port + "/tcp")
    return l


def labels_parser(label):
    return evars_parser(label)


class Rancher:
    def __init__(self, rancher_url, user, passw):
        self.rancher_url = rancher_url
        self.user = user
        self.passw = passw

    def get_stack_name_id(self):
        raw_resp = r.get(self.rancher_url + '/v1/environments', auth=(self.user, self.passw)).json()
        return [{'name': x['name'], "id": x['id']} for x in raw_resp['data']]

    def get_services_in_stack(self, stack_id):
        raw_resp = r.get(self.rancher_url + '/v1/environments/{id}/services'.format(id=stack_id), auth=(self.user, self.passw)).json()
        return [{'name': x['name'], "id": x['id']} for x in raw_resp['data']]

    def get_service_status(self, service_id):
        raw_resp = raw_resp = r.get(self.rancher_url + "/v1/services/" + service_id, auth=(self.user, self.passw)).json()
        return raw_resp['state']

    def create_new_stack(self, stack_name):
        raw_resp = r.post(self.rancher_url + '/v1/environments', auth=(self.user, self.passw), data={"name": stack_name}).json()
        if raw_resp.get('status') == 422:
            raise ValueError("Creating New stack failed", raw_resp)

        return raw_resp

    def create_new_service(self, stack_id, service_name, launch_config):

        payload = json.dumps({"name": service_name, "environmentId": stack_id, "launchConfig": launch_config, "startOnCreate": True})
        raw_resp = r.post(self.rancher_url + '/v1/services', auth=(self.user, self.passw), data=payload).json()

        if raw_resp.get('status') == 422:
            raise ValueError("Creating New service failed", raw_resp)

        while r.get(self.rancher_url + '/v1/services/' + raw_resp['id'], auth=(self.user, self.passw)).json()['state'] == 'active':
            print(r.get(self.rancher_url + '/v1/services/' + raw_resp['id'], auth=(self.user, self.passw)).json()['state'])

        eps = r.get(self.rancher_url + '/v1/services/' + raw_resp['id'], auth=(self.user, self.passw)).json()
        print(r.get(self.rancher_url + '/v1/services/' + raw_resp['id'], auth=(self.user, self.passw)).json()['state'])
        print(eps)
        print("TEST_SERVER_HOST=" + eps['publicEndpoints'][0]['ipAddress'])
        print("TEST_SERVER_PORT=" + str(eps['publicEndpoints'][0]['port']))
        return raw_resp

    def upgrade_service(self, service_id, launch_config):
        resource_path = "/v1/services/{sid}/?action=upgrade".format(sid=service_id)
        payload = json.dumps({"inServiceStrategy": {"launchConfig": launch_config}, "toServiceStrategy": "null"})
        raw_resp = r.post(self.rancher_url + resource_path, data=payload, auth=(self.user, self.passw)).json()

        if raw_resp.get('status') == 422:
            raise ValueError("upgrade failed", raw_resp)

        while(self.get_service_status(service_id) != 'upgraded'):
            pass
        resp = r.post(self.rancher_url + "/v1/services/{sid}/?action=finishupgrade".format(sid=service_id), auth=(self.user, self.passw))
        eps = resp.json()['publicEndpoints'][0]
        print("TEST_SERVER_HOST=" + eps['ipAddress'])
        print("TEST_SERVER_PORT=" + str(eps['port']))

    def deploy(self, stack_name, service_name, env_vars, ports, labels, imageUuid):

        stacks = list(filter(lambda x: x['name'] == stack_name, self.get_stack_name_id()))

        if not stacks:
            stack_id = self.create_new_stack(stack_name)['id']
        else:
            stack_id = stacks[0]['id']

        services = list(filter(lambda x: x['name'] == service_name, self.get_services_in_stack(stack_id)))
        launch_config = self.create_launch_config(imageUuid, env_vars, ports, labels)
        if not services:
            service_id = self.create_new_service(stack_id, service_name, launch_config)['id']
        else:
            service_id = services[0]['id']
            self.upgrade_service(service_id, launch_config)

    def create_launch_config(self, imageUuid, env_vars, ports, labels):
        return {"imageUuid": imageUuid,
                "environment": env_vars,
                "ports": ports,
                "labels": labels,
                "startCount": 1,
                "startOnCreate": True}


if __name__ == '__main__':

    parser = optparse.OptionParser()
    parser.add_option("-e", "--env", help="Set environment variables", metavar="K=V", action="append")
    parser.add_option("--image", help='Deploy the image', metavar="VALUE")
    parser.add_option("--rstack", help='Rancher stack name', metavar="VALUE")
    parser.add_option("--rservice", help='Rancher service name', metavar="VALUE")
    parser.add_option("-p", "--ports", help="Publish a container's port(s) to the host (default [])", metavar="EXT:INT", action="append")
    parser.add_option("-v", "--volume", help="Bind mount a volume (default [])", metavar="EXT:INT", action="append")
    parser.add_option("-n", "--network", help='Connect a container to a network (default "default")', metavar="VALUE")
    parser.add_option("-l", "--label", help=' Set meta data on a container (default [])', metavar="VALUE", action="append")
    (options, args) = parser.parse_args()
    rancher_url = os.environ['RANCHER_URL']
    user = os.environ['RANCHER_USERNAME']
    passw = os.environ['RANCHER_PASSWORD']
    rancher = Rancher(rancher_url, user, passw)
    rancher.deploy(options.rstack, options.rservice, evars_parser(options.env), ports_parser(options.ports), labels_parser(options.label), options.image)
