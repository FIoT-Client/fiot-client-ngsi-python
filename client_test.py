from client import FiwareIotClient


def perseo_test():
    client = FiwareIotClient()

    client.register_device("LDR", "UL_LDR", "LDR001")

    client.subscribe_attributes_change("LDR001", ["luminosity"], "http://192.168.99.100:9090/notices")

    client.create_attribute_change_rule("luminosity", "int", ">100", "http://192.168.1.102:1234/event")

    client.send_observation("UL_LDR", {'l': 80}, protocol='http')
    client.send_observation("UL_LDR", {'l': 120}, protocol='http')


def comet_test():
    client = FiwareIotClient()

    client.register_device("LDR", "UL_LDR", "LDR001")

    client.subscribe_historical_data("LDR001", ["luminosity"])

    client.send_observation("UL_LDR", {'l': 80}, protocol='http')
    client.send_observation("UL_LDR", {'l': 120}, protocol='http')
    client.send_observation("UL_LDR", {'l': 90}, protocol='http')

    client.get_device_historical_data("LDR001", "luminosity", 10)


if __name__ == '__main__':
    perseo_test()
    comet_test()
