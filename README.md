# MQTT

MQTT interface for JemRF sensors : https://www.jemrf.com/collections/all

This application publishes data from RF messages using JSON (example payload below)
to a topic of [device_prefix]_[device id]
The device_prefix is set in the config below
The device id is the devide id of your RF sensor

Example topic  : "myhome/RF_Device04"
Example payload: {"TMP": "25.39", "HUM": "60.20"}
