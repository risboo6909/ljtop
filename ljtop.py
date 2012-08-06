#!/usr/bin/python3.2

import xmlrpc.client
import hashlib

proxy = xmlrpc.client.ServerProxy("http://livejournal.com/interface/xmlrpc")

def call_method(username, password, method_name, **user_params):
	challenge = proxy.LJ.XMLRPC.getchallenge()['challenge']
	hexpass = hashlib.md5(password.encode('utf-8')).hexdigest()	
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
	print (call_method('risboo6909', 'xxx', 'getfriends'))
except Exception as e:
	print (e)

