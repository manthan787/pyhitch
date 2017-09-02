import socket
import click
import os
import pickle
from DiscoveryServiceClient import MyListener
from zeroconf import ServiceBrowser, Zeroconf
import thread


@click.group()
def cli():
    pass


@cli.command()
def list():
    """Lists all the available devices in the network"""
    l = MyListener()
    print l.services

@cli.command()
@click.option("--file", "-f", type=click.Path(exists=True), help="File to be sent")
@click.option("--address", "-a", help="Address of the service")
def send_file(file, address):
    """Allows you to send file to a specified service address"""
    if not os.path.isfile(file):
        raise Exception("Not a file, please provide a path to a file")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, 4000))
    meta = {"filename":os.path.basename(file), "size": os.path.getsize(file)}
    meta = pickle.dumps(meta)
    s.send(meta)
    s.send("<ENDMETA>")
    # send size to the server/receiver
    with open(file, "r") as f:
        content = f.read(1024)
        while True:
            if not content:
                break
            s.send(content)
            content = f.read(1024)
    s.close()


if __name__ == '__main__':
    cli()
