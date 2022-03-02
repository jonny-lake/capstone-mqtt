from multiprocessing.connection import Client
import time
import code
from unicodedata import name
from numpy import var

from opcua import client
from opcua import ua

def embed():
    vars = globals()
    vars.update(locals())
    shell = code.InteractiveConsole(vars)
    shell.interact()

class SubHandler(object):

    def datachange_notification(self, node, val, data):
        print("New data event at NodeID", node, ". New value = ", val)

if __name__ == "__main__":
    # change stuff here
    client = Client("opc.tcp://IP/")
    
    try:
        client.connect()

        # change stuff here
        var1_node = client.get_node('OPCUA stuff')
        var1 = var1_node.get_value()
        var1_setValue = ua.DataValue(ua.Variant(not var1, var1_node.get_data_type_as_variant_type()))
        var1_node.set_value(var1_setValue)

        print(var1_node)

    finally:
        client.disconnect()