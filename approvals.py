import redis
import json
import hmac
import hashlib
from flask import Flask
from flask import request
from flask import Response
from flask import render_template
import time
import datetime
import requests
import pusher

signing_key = '<SCALR_ENDPOINT_KEY>'
app = Flask(__name__)
#pusher_client = pusher.Pusher(
#  app_id='<PUSHER_APP_ID>',
#  key='<PUSHER_KEY>',
#  secret='<PUSHER_SECRET>',
#  cluster='<PUSHER_CLUSTER>',
#  ssl=True
#)

@app.route('/')
def mainfunc():
	return render_template('list.html')

@app.route('/getPending')
def getPending():
	return json.dumps(getRequest('Pending'))

@app.route('/getApproved')
def getApproved():
	return json.dumps(getRequest('Approved'))

@app.route('/getDenied')
def getDenied():
	return json.dumps(getRequest('Denied'))

@app.route('/approveRequest', methods=['POST'])
def approveRequest():
	if 'message' in request.get_json():
		return processRequest('Approved', request.get_json()['requestId'], request.get_json()['message'])
	else:
		return processRequest('Approved', request.get_json()['requestId'], '')

@app.route('/denyRequest', methods=['POST'])
def denyRequest():
	if 'message' in request.get_json():
		return processRequest('Denied', request.get_json()['requestId'], request.get_json()['message'])
	else:
		return processRequest('Denied', request.get_json()['requestId'], '')

@app.route('/approve', methods=['GET', 'POST'])
def approve():
	if request.method == 'POST':
		r = redis.Redis()
		data = request.get_json()
		respdata = {'approval_status': 'pending'}		
		timestamp, signature = sign(respdata)		
		requestId = data['requestId']
		r.sadd('requestId', requestId)
		requestData = { }
		requestData['scalrAccount'] = data['data']['SCALR_ACCOUNT_NAME']
		requestData['scalrFarm'] = data['data']['SCALR_FARM_NAME']
		requestData['user'] = data['data']['SCALR_FARM_OWNER_EMAIL']
		requestData['costCenter'] = data['data']['SCALR_COST_CENTER_NAME']
		requestData['project'] = data['data']['SCALR_PROJECT_NAME']
		requestData['status'] = 'Pending'
		requestData['scalrHost'] = request.remote_addr
		requestData['timestamp'] = time.mktime(datetime.datetime.strptime(timestamp[:-4], '%a %d %b %Y %H:%M:%S').timetuple())
		r.hmset(requestId, requestData)
		response = Response(response=json.dumps(respdata), status=202)
		response.headers['Date'] = timestamp
		response.headers['X-Signature'] = signature
#		pusher_client.trigger('live-approve', 'redis-update', {'message': 'Data changed'})			
		return response 

def sign(data):
	timestamp = datetime.datetime.now().strftime('%a %d %b %Y %H:%M:%S') + ' UTC'
	if(data == ''):
		string = timestamp 
	else:
		string = json.dumps(data) + timestamp
	signature = hmac.new(signing_key.encode('utf-8'), string.encode('utf-8'), hashlib.sha1).hexdigest()
	return timestamp, signature

def getRequest(status):
	r = redis.Redis()
	requestList = []
	for item in r.smembers('requestId'):
		if r.hlen(item) > 0 and r.hexists(item, 'status'):
			if r.hmget(item, 'status')[0].decode('UTF-8') == status:
				requestItem = {
					'requestId': item.decode('UTF-8'),
					'user': r.hmget(item, 'user')[0].decode('UTF-8'),
					'scalrFarm': r.hmget(item, 'scalrFarm')[0].decode('UTF-8'),
					'businessUnit': r.hmget(item, 'scalrAccount')[0].decode('UTF-8'),
					'costCenter': r.hmget(item, 'costCenter')[0].decode('UTF-8'),
					'project': r.hmget(item, 'project')[0].decode('UTF-8'),
					'timestamp': r.hmget(item, 'timestamp')[0].decode('UTF-8')
					}
				if r.hexists(item, 'message'):
					requestItem['message'] = r.hmget(item, 'message')[0].decode('UTF-8')
				requestList.append(requestItem)
	return requestList

def processRequest(status, requestId, message):
	r = redis.Redis()
	data = {'approval_status': status.lower(), 'message': message }
	timestamp, signature = sign(data)
	headers = {'Content-Type': 'application/json', 'Date': timestamp, 'X-Signature': signature}
	response = requests.post('https://' + r.hmget(requestId, 'scalrHost')[0].decode('UTF-8') + '/integration-hub/callback/' + requestId, json=data, headers=headers, verify=False)
	r.hset(requestId, 'status', status)
	r.hset(requestId, 'message', message)
	r.hset(requestId, 'timestamp', time.mktime(datetime.datetime.strptime(timestamp[:-4], '%a %d %b %Y %H:%M:%S').timetuple()))
#	pusher_client.trigger('live-approve', 'redis-update', {'message': 'Data changed'})

	return status		
