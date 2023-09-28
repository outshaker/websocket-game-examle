from setuptools import setup, find_packages

setup(
    name='websocket-game-example',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'websockets',
    ],
)