from setuptools import setup
import sys

options = {}

if sys.platform == 'darwin':
    dist_dependency = ['py2app']
    options = {'py2app': {'iconfile': 'data/hitch.icns'}}
elif sys.platform == 'win32':
    dist_dependency = ['py2exe']
else:
    dist_dependency = []



setup(
    name="Hitch",
    version="1.0",
    description="Closs-platform file transfer on local network",
    author="Manthan Thakar",
    app = ["app.py"],
    data_files=["data/hitch_icon.ico"],
    setup_requires = [
        "click",
        "tqdm",
        "zeroconf"
    ] + dist_dependency,
    options=options
)
