#!/usr/bin/env python
import requests as r
import json
import sys
import ast
import os


class Rancher:
    def __init__(self, rancher_url, user, passw):
        self.rancher_url = rancher_url
        self.user = user
        self.passw = passw

    def get_stack_name_id(self):
        raw_resp = r.get(self.rancher_url + '/v1/environments').json()
        return [{'name': x['name'], "id": x['id']} for x in raw_resp['data']]

    def get_services_in_stack(self, stack_id):
        raw_resp = r.get(self.rancher_url + '/v1/environments/{id}/services'.format(id=stack_id)).json()
        return [{'name': x['name'], "id": x['id']} for x in raw_resp['data']]

    def get_service_status(self, service_id):
        raw_resp = raw_resp = r.get(self.rancher_url + "/v1/services/" + service_id).json()
        return raw_resp['state']

    def create_new_stack(self, stack_name):
        raw_resp = r.post(self.rancher_url + '/v1/environments', auth=(self.user, self.passw), data={"name": stack_name}).json()
        if raw_resp.get('status') == 422:
            raise ValueError("Creating New stack failed", raw_resp)

        return raw_resp

    def create_new_service(self, stack_id, service_name, imageUuid, env_vars, ports):
        raw_resp = r.post(self.rancher_url + '/v1/services', auth=(self.user, self.passw),
                          data=json.dumps({"name": service_name, "environmentId": stack_id,
                                           "launchConfig": {"imageUuid": imageUuid, "environment": env_vars,
                                                            "startCount": 1, "ports": ports}, "startOnCreate": True})).json()

        if raw_resp.get('status') == 422:
            raise ValueError("Creating New service failed", raw_resp)

        return raw_resp

    def upgrade_service(self, service_id, imageUuid, env_vars, ports):

        raw_resp = r.post(self.rancher_url + "/v1/services/{sid}/?action=upgrade".format(sid=service_id), data=json.dumps(
            {"inServiceStrategy": {"launchConfig": {"imageUuid": imageUuid, "environment": env_vars, "ports": ports}}, "toServiceStrategy": "null"})).json()
        if raw_resp.get('status') == 422:
            raise ValueError("upgrade failed", raw_resp)

        while(self.get_service_status(service_id) != 'upgraded'):
            pass
        r.post(self.rancher_url + "/v1/services/{sid}/?action=finishupgrade".format(sid=service_id))

    def deploy(self, stack_name, service_name, env_vars, ports, imageUuid):

        stacks = list(filter(lambda x: x['name'] == stack_name, self.get_stack_name_id()))

        if not stacks:
            stack_id = self.create_new_stack(stack_name)['id']
        else:
            stack_id = stacks[0]['id']

        services = list(filter(lambda x: x['name'] == service_name, self.get_services_in_stack(stack_id)))
        if not services:
            service_id = self.create_new_service(stack_id, service_name, imageUuid, env_vars, ports)['id']
        else:
            service_id = services[0]['id']
            self.upgrade_service(service_id, imageUuid, env_vars, ports)

if __name__ == '__main__':

    if len(sys.argv) != 6:
        print("Usage: ./rancher_deploy stack_name service_name env_vars ports imageUuid")
        exit(1)
    else:
        stack_name = sys.argv[1]
        service_name = sys.argv[2]
        env_vars = ast.literal_eval(sys.argv[3])
        ports = ast.literal_eval(sys.argv[4])
        imageUuid = sys.argv[5]
        rancher_url = os.environ['RANCHER_URL']
        user = os.environ['RANCHER_USERNAME']
        passw = os.environ['RANCHER_PASSWORD']
        rancher = Rancher(rancher_url, user, passw)
        rancher.deploy(stack_name, service_name, env_vars, ports, imageUuid)
