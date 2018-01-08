**************************************************
Welcome to the FIoT-Client Python Documentation!
**************************************************

.. contents::
   


.. toctree::
	:caption: Theme



.. _authors:

Authors
=======

- **Lucas Cristiano Calixto Dantas** - Initial work and developer
- **Lucas Ramon Bandeira da Silva** - Project collaborator
- **Carlos Eduardo da Silva** - Professor advisor


.. _introduction:

Introduction
============
The FIoT-Client Python is a Python library that eases the use of IoT and Context APIs from FIWARE platform. The functions of each file of the library are listed in alphabetical order.


.. _FunctionList: 

Function List
=============

utils.py
---------

merge_dicts()
^^^^^^^^^^^^^

**merge_dicts(dict_args)**

Merge two dicts into a single dictionary. The argument is the dicts to be merged, and the function returns the resulting dictionary from the merge 

read_config_file()
^^^^^^^^^^^^^^^^^^

**read_config_file(config_file)**

Load configuration file and creates a dict with the necessary attributes. The argument is the file to be read, and the function returns a dict with the attributs read from the file.

init.py
-------

authenticate()
^^^^^^^^^^^^^^

**authenticate(self, username, password)**

Creates an authentication token based on user credentials using FIWARE Lab OAuth2.0 Authentication system. If you didn't have a user, go and register first at `http://cloud.fiware.org <http://cloud.fiware.org>`__ . The arguments of this function are the username and password of the user from Fiware authentication account, and returns the generated token and expiration.

generate_api_key()
^^^^^^^^^^^^^^^^^^

**generate_api_key()**

Generate a random api key to be used on service creation. This function doesn't have arguments and return the generated api key string.

_send_request()
^^^^^^^^^^^^^^^

**_send_request(self, url, payload, method, additional_headers=None)**

Auxiliary method to configure and execute a request to FIWARE APIs. The arguments of this function are the url to be called on the request, the payload to be sent on the request, the method to be used on the request and additional http headers to be used in the request. This function returns the response from the request execution.

set_service()
^^^^^^^^^^^^^

**set_service(self, service, service_path)**

Specify the service context to use on operations. The arguments of this function are the name of the service to be used and the service path of the service to be used. This function has no returns.


context.py
----------

ĉreate_attribute_change_rule()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**create_attribute_change_rule(self, attribute, attribute_type, condition, action='post', notification_url=None)**

Register a new rule to be evaluated on attribute values change and a action to be taken when rule evaluated to true. The arguments of the function are the attribute to be monitored, the type of the attribute to be monitored, the condition to be evaluated on changes on attribute's value, the action type to be taken when condition is evaluated true (Currently accepted values to this parameter are 'email' and 'post') and the endpoint to which POST notifications will be sent. This function returns the information of the created rule.

get_entities_by_type()
^^^^^^^^^^^^^^^^^^^^^^

**get_entities_by_type(self, entity_type)**

Get entities from its entity type. The argument of this function is the type of the entities to be searched, and returns a list with the information of the entities found with the given type.

get_entity_by_id()
^^^^^^^^^^^^^^^^^^
**get_entity_by_id(self, entity_id)**

Get an entity information from its entity id. The argument of this function is the id of the entity to be searched, and returns the information of the entity found with the given id or None if no entity was found with the id.

get_historical_data()
^^^^^^^^^^^^^^^^^^^^^

**get_historical_data(self, entity_type, entity_id, attribute, items_number=10)**

Get historical data from a specific attribute of an entity. The arguments of this function are the type of the entity to get historical data, the id of the entity to get historical data, the attribute of the entity to get historical data, and the number of last entries to be queried (If no value is provided, the default value (10 entries) will be used). This function returns the historical data on the specified attribute of the given entity.

get_subscription_by_id()
^^^^^^^^^^^^^^^^^^^^^^^^
**get_subscription_by_id(self, subscription_id)**

Get subscription information from its subscription id. The argument of the function is the id of the subscription to be searched, and returns the information of the subscription found with the given id, or None if no subscription was found with the id.

list_subscriptions()
^^^^^^^^^^^^^^^^^^^^

**list_subscriptions(self)**

Get all subscriptions. This function has no arguments and returns a list with the ids of all the subscriptions.

subscribe_attributes_change()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**subscribe_attributes_change(self, device_id, attributes, notification_url)**

Create a new subscription on given attributes of the device with id specified. The arguments of this function are the id of the device to be monitored, the list of attributes do be monitored and the URL to which the notification will be sent on changes. This function returns the information of the subscription.

subscribe_cygnus()
^^^^^^^^^^^^^^^^^^

**subscribe_cygnus(self, entity_id, attributes)**

Create a new subscription on attributes to send changes on its values to Cygnus. The arguments of this function are the id of the entity to be monitored, the list of attributes do be monitored and returns the information of the subscription.

subscribe_historical_data()
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**subscribe_historical_data(self, entity_id, attributes)**

Create a new subscription on attributes to store changes on its values as historical data. The parameters of this function are the id of the entity to be monitored and the list of attributes do be monitored, and returns the information of the subscription.

unsubscribe()
^^^^^^^^^^^^^

**unsubscribe(self, subscription_id)**

Remove a subscription with the given subscription id. The paramater of this function is the id of the subscription to be removed, and returns True if the subscription with the given id was removed False if no subscription with the given id was removed.



iot.py
------

create_service()
^^^^^^^^^^^^^^^^

**create_service(self, service, service_path, api_key=None)**

Creates a new service with the given information. The arguments of this function are the name of the service to be created, the service path of the service to be created and a specific api key to use to create the service (if no api key is provided, a random one will be generated). The function returns the information of the created service.

_create_service()
^^^^^^^^^^^^^^^^^

**_create_service(self, service, service_path, api_key)**

Auxiliary method to try to create a service with the given information, and the arguments are the name of the service to be created, the service path of the service to be created and the api key to use to create the service. The function returns the response of the creation request.

_create_ul_payload()
^^^^^^^^^^^^^^^^^^^^

**_create_ul_payload_from_measurements(measurements)**

Auxiliary method to create a UL formatted payload string from measurement group or a list of measurement groups to the FIWARE platform from a  device. the argument of this function is a measurement group (a dict where keys are device attributes and values are measurements for each attribute) or a list of measurement groups obtained in the device, and returns UL formatted payload string from measurement group.

get_polling_commands()
^^^^^^^^^^^^^^^^^^^^^^

**get_polling_commands(self, device_id, measurements)**

Get a list of polling commands of the device with the given id when sending a measurement group or a list of measurement groups to the FIWARE platform from a device with POST request. The parameters of this function are the id of the device to verify pooling commands and a measurement group (a dict where keys are device attributes and values are measurements for each attribute) or a list of measurement groups obtained in the device. The function returns the list of pooling commands of the device.

register_device()
^^^^^^^^^^^^^^^^^

**register_device(self, device_schema, device_id, entity_id, endpoint='', protocol='IoTA-UL')**

Register a new device with the given structure in the currently selected service. this function has the following arguments: a JSON string representing device schema, the id to the device to be created, the id to the NGSI entity created representing the device, the endpoint of the device to which actions will be sent on format IP:PORT and the protocol to be used on device registration. (If no value is provided the default protocol (IoTA-UL) will be used). this function returns the Information of the registered device.

register_device_from_file()
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**register_device_from_file(self, device_file_path, device_id, entity_id, endpoint='', protocol='IoTA-UL')**

Register a new device with the given structure in the currently selected service. this function has the following arguments: the path to the description file for the device, the id to the device to be created, the id to the NGSI entity created representing the device, the endpoint of the device to which actions will be sent on format IP:PORT and the protocol to be used on device registration. (If no value is provided the default protocol (IoTA-UL) will be used). this function returns the Information of the registered device.

remove_device()
^^^^^^^^^^^^^^^

**remove_device(self, device_id)**

Removes a device with the given id in the currently selected service, the argument of this function is the id to the device to be removed and returns a response of the removal request.

remove_service()
^^^^^^^^^^^^^^^^

**remove_service(self, service, service_path, api_key="", remove_devices=False)**

Remove a subservice into a service (If Fiware-ServicePath is "/*" or "/#" remove service and all subservices). The arguments of this function are the name of the service to be removed, the service path of the service to be removed, the api key of the service, and the parameter "remove_devices", in which it is a boolean that defines if either its to remove devices in service/subservice or not (If no value is provided, the default value (False) will be used).

.. note::
	This parameter is not valid when Fiware-ServicePath is '/*' or '/#'.

this function returns the response of the removal request.

send_command()
^^^^^^^^^^^^^^

**send_command(self, entity_id, device_id, command, params=None)**

Sends a command to a device the FIWARE platform (http://fiware-orion.readthedocs.io/en/latest/user/walkthrough_apiv1/index.html#ngsi10-standard-operations at "Update context elements" section). The arguments of this function are the id of the entity that represents the device, the id of the device to which the command will be sent, the name of the command to be called on the device and the command parameters to be sent. The function returns the result of the command call.

send_observation()
^^^^^^^^^^^^^^^^^^

**send_observation(self, device_id, measurements, protocol='MQTT')**

Sends a measurement group or a list of measurement groups to the FIWARE platform from a device. The arguments of this function are the id of the device in which the measurement was obtained, a measurement group (a dict where keys are device attributes and values are measurements for each attribute) or a list of measurement groups obtained in the device and the transport protocol to be used to send measurements. Currently accepted values are 'MQTT' and 'HTTP'.

.. note::
	If no value is provided the default value (MQTT) will be used

This function returns the summary of the sent measurements.

set_api_key()
^^^^^^^^^^^^^

**set_api_key(self, api_key)**

Sets the api key to use to send measurements from device. The argument of the function is the api key of the service to use and this function has no returns.
