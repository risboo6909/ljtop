#!/usr/bin/python3.2

import xmlrpc.client
import hashlib

from optparse import OptionParser

proxy = xmlrpc.client.ServerProxy("http://livejournal.com/interface/xmlrpc")

def call_method(username, password, method_name, **user_params):	

	if password.startswith('md5:'):
		# use md5 hash of password
		hexpass = password[4:]		
	else:
		hexpass = hashlib.md5(password.encode('utf-8')).hexdigest()

	challenge = proxy.LJ.XMLRPC.getchallenge()['challenge']	
	response = hashlib.md5((challenge + hexpass).encode('utf-8')).hexdigest()
	params =	{
					'auth_method': 'challenge',
					'username': username,
					'auth_challenge': challenge,
					'auth_response': response,
					'ver': 1
				}
	params.update(user_params)
	try:
		method = getattr(proxy.LJ.XMLRPC, method_name)
	except:
		raise

	return method(params)

try:
	print (call_method('risboo6909', 'md5:15faeadc6c85cc0e82518b09e7e8a92d', 'getfriends'))
except Exception as e:
	print (e)

