import fileinput
import requests
import string
import json
import sys


def __main__():
	for line in sys.stdin:
		if line is None or len (line) < 1:
			continue
		line = cleanString (line)
		print ('got line "' + line + '"')
		keyValuePair = messageToKeyValuePair (line)
		if keyValuePair is None or len (keyValuePair) != 2:
			continue
		key, value = keyValuePair
		if key == 'POS1':
			handleGarageDoorSensor (key, value)

def updateStatus (id, description, status):
	headers = { 'Content-Type': 'application/json', 'Authorization': '189728734tndaotehi787' } 
	payload = json.dumps ({ "Description": description, "Status": status })
	print (payload)
	result = requests.put ('http://www.nickeasler.com/api/status/' + id, headers=headers, data=payload)
	print (result)

def cleanString (toClean):
	result = ''
	for x in toClean:
		if x in string.printable and x not in ('\r', '\n'):
			result += x
	return result

def messageToKeyValuePair (message):
	pair = message.split ('_')
	if (len (pair) != 2):
		return None
	cleanKey = cleanString (pair [0])
	cleanValue = cleanString (pair [1])
	return (cleanKey, cleanValue)

def handleGarageDoorSensor (key, value):
	description = 'Garage door'
	if (value == '0'):
		updateStatus (key, description, 'Closed')
	else:
		updateStatus (key, description, 'Open')


__main__()
