from setuptools import setup

setup(name='RancherDeploy',
      version='0.1',
      description='The funniest joke in the world',
      packages=['RancherDeploy'],
      install_requires=['requests', 'click'],
      entry_points = { 'console_scripts' : ['RancherDeploy=RancherDeploy:main']},
      zip_safe=False)