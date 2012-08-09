#!/usr/bin/python3.2

import xmlrpc.client
import hashlib
import os

from optparse import OptionParser

username = 'risboo6909'
password = 'md5:15faeadc6c85cc0e82518b09e7e8a92d'

proxy = xmlrpc.client.ServerProxy("http://livejournal.com/interface/xmlrpc")

class MyDict(dict):

	def __init__(self):
		dict.__init__(self)		

	def update(self, another_dict):
		for k, v in another_dict.items():
			if k in self.keys():
				self[k] += v
			else:
				self[k] = v

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

def get_call_func(username, password):	
	return lambda method_name, **user_params: call_method(username, password, method_name, **user_params)

def count_posts(raw_data):
	output = MyDict()
	for item in raw_data:
		if type(item) is dict:			
			if 'identity_type' not in item and 'postername' in item:
				output.setdefault(item['postername'], 0)
				output[item['postername']] += 1
			elif 'identity_type' in item and 'identity_display' in item:
				output.setdefault(item['identity_display'], 0)
				output[item['identity_display']] += 1
			if 'children' in item:
				output.update(count_posts(item['children']))
	return output

def generate_HTML(chart_data, username):

	body = """
<html>
	<body>
		<b> Top commenters for %s</b>
			<br>
			<br>
			""" % username

	filename = username + '.html'
	f = open(filename, 'wt')	

	for item in chart_data:
		body += '%s ... %s<br>' % (item[0], item[1])

	body += """
	<br>
	<br>
	git clone https://github.com/risboo6909/ljtop.git, to get the latest version of ljtop.py
	</body>
</html>
			"""

	f.write(body)
	f.close()


f = get_call_func(username, password)

print ('Fetching data...')

try:
	events = f('getevents', selecttype = 'lastn', howmany = 100)
except Exception as e:
	print (e)
	os._exit(1)

chart = MyDict()
for item in events['events']:	
	comments = f('getcomments', itemid = item['itemid'])
	chart.update(count_posts(comments['comments']))

print ('done!')

print ('Building chart...')
chart = sorted((list(chart.items())), key = lambda item: item[1], reverse = True)
print ('done!')

print (chart)

generate_HTML(chart, username)
