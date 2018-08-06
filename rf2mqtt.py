#!/usr/bin/env python
"""
rf2mqtt.py v1 Serial to MQTT message broker
---------------------------------------------------------------------------------
                                                                                  
 J. Evans August 2018
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
 WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
 CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                                                       
                                                                                  
 Revision History                                                                  
 V1.00 - Release
 
 Instructions:
 
 This application publishes data from RF messages using JSON (example payload below)
 to a topic of [topic]/[device_prefix]_[device id]
 The topic is set in the config below
 The device_prefix is set in the config below
 The device id is the device id of your RF sensor
 
 Example topic  : "myhome/RF_Device04"
 Example payload: {"TMP": "25.39", "HUM": "60.20"}
 
"""

import serial
import time
import sys
import thread
import logging
import json
import argparse
from random import randint
from time import sleep
global RFList
global LocationList
global numrf
import paho.mqtt.client as paho

#Configurations===============
DEBUG = True
Fahrenheit = False
mqtt_server = "192.168.2.201" #Enter the IP address of your MQTT server in between the quotes
topic = "myhome"
device_prefix = "RF_Device"
#=============================

def dprint(message):
	if (DEBUG):
		print message

def ProcessMessageThread(value, value2, DevId, type, property):
	try:
			thread.start_new_thread(ProcessMessage, (value, value2, DevId, type, property ) )
	except:
			print "Error: unable to start thread"

def mqtt_publish(device_id, value, property, value2):
	data = {}
	data[property] = value;
	dprint(property)
	dprint(value2)
	if (property=="TMP" and value2!=0):
		data['HUM'] = value2
	json_data = json.dumps(data)
	dprint(device_id)
	dprint(json_data)
	client = paho.Client("pi_rf_"+str(randint(0, 100)))
	client.connect(mqtt_server, port=1883)
	client.publish(topic+"/"+device_id, json_data)
	client.disconnect()
			
def ProcessMessage(value, value2, DevId, type, property):
# Notify the host that there is new data from a sensor (e.g. door open)
	try:
		dprint("Processing data : DevId="+str(DevId)+",Type="+str(type)+",Value1="+str(value)+",Value2="+str(value2))

		DevId=device_prefix+DevId;
		#Send switch sensor value to host
		if type==1:
				value=value[1:]
				if value=='OF' or value=='OFF':
						mqtt_publish(DevId, "Open", property,0)
				if value=='ON':
						mqtt_publish(DevId, "Closed", property,0)

		#Send battery level to host
		if type==2:
				mqtt_publish(DevId, value, property,0)

		#Send temperature to host
		if type==3:
				if Fahrenheit:
						value = value*1.8+32
						value = round(value,2)
				
				mqtt_publish(str(DevId), str(value), property,0)

		#Send humidity to host
		if type==4:
				if Fahrenheit:
						value = value*1.8+32
						value = round(value,2)
				
				mqtt_publish(DevId, str(value), "TMP", str(value2))
				
				
	except Exception as e: dprint(e)
	return(0)

def main():
        currvalue=''
        tempvalue=-999;
        
        # loop until the serial buffer is empty

        start_time = time.time()
        
        #try:
        while True:

				# declare to variables, holding the com port we wish to talk to and the speed
				port = '/dev/ttyAMA0'
				baud = 9600

				# open a serial connection using the variables above
				ser = serial.Serial(port=port, baudrate=baud)

				# wait for a moment before doing anything else
				sleep(0.2)        
				while ser.inWaiting():
						# read a single character
						char = ser.read()
						# check we have the start of a LLAP message
						if char == 'a':
								sleep(0.01)
								start_time = time.time()
								
								# start building the full llap message by adding the 'a' we have
								llapMsg = 'a'

								# read in the next 11 characters form the serial buffer
								# into the llap message
								llapMsg += ser.read(11)

								# now we split the llap message apart into devID and data
								devID = llapMsg[1:3]
								data = llapMsg[3:]
								
								dprint(time.strftime("%c")+ " " + llapMsg)
																
								if data.startswith('BUTTON'):
										sensordata=data[5:].strip('-')
										if currvalue<>sensordata or currvalue=='':
												currvalue=sensordata
												ProcessMessage(currvalue, 0, devID,1, "BUTTON")

								if data.startswith('BTN'):
										sensordata=data[2:].strip('-')
										if currvalue<>sensordata or currvalue=='':
												currvalue=sensordata
												ProcessMessage(currvalue, 0, devID,1, "BUTTON")

								if data.startswith('TMPA'):
										sensordata=str(data[4:].rstrip("-"))								
										currvalue=sensordata
										ProcessMessage(currvalue, 0, devID,3, "TMPA")
								
								if data.startswith('ANAA'):
										sensordata=str(data[4:].rstrip("-"))								
										currvalue=sensordata
										ProcessMessage(currvalue, 0, devID,3, "ANAA")
								
								if data.startswith('ANAB'):
										sensordata=str(data[4:].rstrip("-"))								
										currvalue=sensordata
										ProcessMessage(currvalue, 0, devID,3, "ANAB")
								
								if data.startswith('TMPC'):
										sensordata=str(data[4:].rstrip("-"))								
										currvalue=sensordata
										ProcessMessage(currvalue, 0, devID,3, "TMPC")
								
								if data.startswith('TMPB'): #Temperature followed by humidity
										sensordata=str(data[4:].rstrip("-"))								
										tempbdata=sensordata
																				
								if data.startswith('HUM'):
										sensordata=str(data[3:].rstrip("-"))								
										currvalue=sensordata
										if tempbdata<>"" and sensordata<>"":
											ProcessMessage(tempbdata, sensordata, devID,4, "")
											tempbdata=''
												
								# check if battery level is being sent axxBATTn.nn-
								if data.startswith('BATT'):
										sensordata=data[4:].strip('-')
										currvalue=sensordata 
										ProcessMessage(currvalue, 0, devID,2, "BATT")
				elapsed_time = time.time() - start_time
				if (elapsed_time > 2):
						currvalue=""
						sensordata=""
						tempbdata=""
				#sleep(0.2)
				#except:
				#        print "Error: unable to start thread"
           
if __name__ == "__main__":
        main()



   
   


