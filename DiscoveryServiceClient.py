from zeroconf import ServiceBrowser, Zeroconf
import socket


class MyListener(object):

    def __init__(self):
        self.services = {}

    def remove_service(self, zeroconf, type, name):
        print("Service %s removed" % (name,))

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if not info:
            return
        device = info.properties['device']
        if device != socket.gethostname():
            self.services[device] = info
            print self.services
            print("Service %s added, service info: %s" % (name, info))

if __name__ == '__main__':
    zeroconf = Zeroconf()
    listener = MyListener()
    browser = ServiceBrowser(zeroconf, "_discovery._tcp.local.", listener)
    try:
        input("Press enter to exit...\n\n")
    finally:
        zeroconf.close()
