
import time
import code

from opcua import Client
from opcua import ua
# def embed():
#     vars = globals()
#     vars.update(locals())
#     shell = code.InteractiveConsole(vars)
#     shell.interact()


# class SubHandler(object):

#     def datachange_notification(self, node, val, data):
#         print("New data event at NodeID", node, ". New value = ", val)

if __name__ == "__main__":
    # change stuff here
    client = Client("opc.tcp://192.168.0.1:4840/", timeout=10)
    try:
        client.connect()

        # change stuff here
        var1_node = client.get_node('ns=3;s="OPC"."PLCstate"')
        var1 = var1_node.get_value()
        var1_setValue = ua.DataValue(ua.Variant(not var1, var1_node.get_data_type_as_variant_type()))
        var1_node.set_value(var1_setValue)

        print(var1_node)

    finally:
        client.disconnect()