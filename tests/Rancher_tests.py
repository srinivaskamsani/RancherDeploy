from RancherDeploy.Rancher import Rancher
from RancherDeploy.Service import Service
import os
import time


user = os.getenv("RANCHER_USER")
password = os.getenv("RANCHER_PASS")
rancher_url = os.getenv("RANCHER_URL")
api_version = os.getenv("RANCHER_API_VERSION")

def test_create_new_stack():
    
    new_stack_name = "RancherDeployTest"
    rancher = Rancher(rancher_url, (user, password), api_version)

    # Make sure the stack doesn't exist before we create it
    assert new_stack_name not in rancher.stacks
    
    rancher.create_new_stack(new_stack_name)

    assert new_stack_name in rancher.stacks

    test_stacks = list(filter(lambda x: x=="RancherDeployTest", rancher.stacks))
    assert len(test_stacks) == 1

    # clean up
    test_stacks[0].remove()

test_create_new_stack()

def test_create_new_service():

    rancher = Rancher(rancher_url, (user, password), api_version)
    new_stack_name = "RancherDeployTest"
    
    expected_service = Service(None, (user, password))
    expected_service.name = 'RancherDeployTest'
    expected_service.image_name = 'tutum/hello-world'
    expected_service.scale = 1
    expected_service.env_vars = {'var1': 'val1'}
    expected_service.labels = {'label1' : 'val2'}
    expected_service.ports = ['80/tcp']

    rancher.create_new_stack(new_stack_name)
    test_stacks = list(filter(lambda x: x=="RancherDeployTest", rancher.stacks))
    test_stacks[0].create_new_service(expected_service)

    time.sleep(10)
    test_services = list(filter(lambda x: x=="RancherDeployTest",test_stacks[0].services))

    actual_service = test_services[0]
    
    assert actual_service.name == expected_service.name
    assert actual_service.image_name == expected_service.image_name
    assert actual_service.scale == expected_service.scale
    assert actual_service.env_vars == expected_service.env_vars
    assert actual_service.labels == expected_service.labels
    
    actual_service.remove()
    test_stacks[0].remove()

test_create_new_service()

def test_upgrade_service():
    rancher = Rancher(rancher_url, (user, password), api_version)
    new_stack_name = "RancherDeployTest"
    
    s = Service(None, (user, password))
    s.name = 'RancherDeployTest'
    s.image_name = 'tutum/hello-world'
    s.scale = 1
    s.env_vars = {'var1': 'val1'}
    s.labels = {'label1' : 'val2'}
    s.ports = ['80/tcp']

    rancher.create_new_stack(s)
    test_stacks = list(filter(lambda x: x=="RancherDeployTest", rancher.stacks))
    test_stacks[0].create_new_service(s)

    time.sleep(10)
    test_services = list(filter(lambda x: x=="RancherDeployTest",test_stacks[0].services))

    actual_service = test_services[0]
    actual_service.env_vars = {'var2':'val2'}
    actual_service.upgrade()
    
    assert actual_service.name == s.name
    assert actual_service.image_name == s.image_name
    assert actual_service.scale == s.scale
    assert actual_service.env_vars == {'var2' : 'val2'}
    assert actual_service.labels == s.labels
    
    actual_service.remove()
    test_stacks[0].remove()

test_upgrade_service()
