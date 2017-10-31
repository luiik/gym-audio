from setuptools import setup

setup(name='gym_frogger',
      version='0.0.1',
      install_requires=['gym','pygame'], # And any other dependencies foo needs
      packages=['gym_frogger'],
      package_data={'gym_frogger': ['envs/data/*.png','envs/data/*.wav']},
)
