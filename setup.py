from setuptools import setup

setup(name='RancherDeploy',
      version='0.1',
      description='A script to deploy services to Rancher',
      packages=['RancherDeploy'],
      install_requires=['requests', 'click'],
      entry_points = { 'console_scripts' : ['RancherDeploy=RancherDeploy:main']},
      zip_safe=False)