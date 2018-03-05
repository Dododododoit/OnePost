from setuptools import setup

setup(
    name='onepost',
    version='0.1.0',
    packages=['onepost'],
    include_package_data=True,
    install_requires=[
        'Flask==0.12.2',
        'sh==1.12.14',
        'InstagramApi',
        'oauth2',
        'python-twitter',
        'pytumblr',
    ],
)
