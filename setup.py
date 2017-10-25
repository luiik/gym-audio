from setuptools import setup

setup(name='gym_audio',
      version='0.0.1',
      install_requires=['gym','pygame'], # And any other dependencies foo needs
      packages=['gym_audio'],
      package_data={'gym_audio': ['envs/data/*.png']},
)
