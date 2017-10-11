from RancherDeploy.Rancher import Rancher
import os

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




