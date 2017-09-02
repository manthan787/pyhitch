from zeroconf import ServiceInfo, Zeroconf, InterfaceChoice
import socket
from config import (DISCOVERY_SERVICE_PORT, DISCOVERY_SERVICE_TYPE,\
                    DISCOVERY_SERVICE_NAME)
from contextlib import contextmanager


def get_ip_address():
    """A hack to get the IP address of the active interface
    without knowing the name of the network interface.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def get_server(service_type, service_name, ip, port):
    info = add_service(service_type, service_name, ip, port)
    print info
    zeroconf = Zeroconf(interfaces=InterfaceChoice.All)
    zeroconf.register_service(info)
    return zeroconf


def add_service(service_type, service_name, address, port):
    device_name = socket.gethostname()
    return  ServiceInfo(service_type, "{}.{}".format(device_name, service_type),
            address=socket.inet_aton(address),
            port=port,
            weight=0,
            priority=0,
            properties={"device": device_name},
            server=None)


def serve(service_type, service_name, ip, port):
    try:
        z = get_server(service_type, service_name, ip, port)
        input("Press enter to exit...\n")
    finally:
        z.unregister_all_services()
        z.close()

if __name__ == '__main__':
    ip = get_ip_address()
    serve(DISCOVERY_SERVICE_TYPE, DISCOVERY_SERVICE_NAME, ip,
                    DISCOVERY_SERVICE_PORT)
