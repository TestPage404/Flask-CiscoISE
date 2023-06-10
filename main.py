from flask import Flask, render_template, request, redirect, jsonify, flash, session, url_for
import requests
import json
import random
import arrow
import os
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = config.shared_secret


class User:
	def __init__(self, username, password):
		self.username = username
		self.password = password


users = []


def GetRandomNumber():
	Random_Number = random.randint(291438764213, 984132987431)
	return Random_Number


def CreateISEUser(samaccountname, period):
	url = f"https://{config.ip}:9060/ers/config/internaluser"
	ise_user_password = GetRandomNumber()
	# expiration_date = arrow.now().shift(days=period).date()
	payload = json.dumps({
		"InternalUser": {
			"name": samaccountname,
			"description": ise_user_password,
			"enabled": True,
			"email": samaccountname + "@obghk.ru",
			"password": ise_user_password,
			"changePassword": False,
			"identityGroups": "a1740510-8c01-11e6-996c-525400b48521",
			"expiryDateEnabled": True,
			"expiryDate": str(period),
			"passwordIDStore": "Internal Users"
		}
	})
	headers = {
		'Accept': 'application/json',
		'Content-Type': 'application/json',
		'Authorization': 'Basic Z29kb2ZhcGk6V2F1bXo5NHNjSA==',
		'Cookie': 'APPSESSIONID=EACA76E8921B03ABBB1DC5481F10771C; JSESSIONIDSSO=F91298A14A8742C8E41E18E8031041D7'
	}
	response = requests.request("POST", url, headers=headers, data=payload, verify=False)


def FetchFromISE(id):
	url = f"https://{config.ip}:9060/ers/config/internaluser/?filter=email.CONTAINS." + id

	payload = {}
	headers = {
		'Accept': 'application/json',
		'Content-Type': 'application/json',
		'Authorization': 'Basic Z29kb2ZhcGk6V2F1bXo5NHNjSA==',
		'Cookie': 'APPSESSIONID=39CA9453A74728BE5CB3DA6610829DC1; JSESSIONIDSSO=87978D01CEC651AEEA9AC3F05CAA6B42'
	}
	response = requests.request("GET", url, headers=headers, data=payload, verify=False)
	jsonData = response.text
	dictData = json.loads(jsonData)
	clear_data = dictData["SearchResult"]["resources"]
	try:
		ise_user_password = str(clear_data[0].get("description"))
		ise_user = str(clear_data[0].get("name"))
		return ise_user, ise_user_password
	except:
		ise_user_password = None


def AccountCount():
	email = '@obghk.ru'
	url = f"https://{config.ip}:9060/ers/config/internaluser/?filter=email.CONTAINS." + email
	payload = {}
	headers = {
		'Accept': 'application/json',
		'Content-Type': 'application/json',
		'Authorization': 'Basic Z29kb2ZhcGk6V2F1bXo5NHNjSA==',
		'Cookie': 'APPSESSIONID=39CA9453A74728BE5CB3DA6610829DC1; JSESSIONIDSSO=87978D01CEC651AEEA9AC3F05CAA6B42'
	}
	response = requests.request("GET", url, headers=headers, data=payload, verify=False)
	jsonData = response.text
	dictData = json.loads(jsonData)
	clear_data = dictData["SearchResult"]["total"]
	return clear_data


def RemoveISEuser(ise_user):
	url = f"https://{config.ip}:9060/ers/config/internaluser/name/{ise_user}"
	payload = {}
	headers = {
		'Accept': 'application/json',
		'Content-Type': 'application/json',
		'Authorization': 'Basic Z29kb2ZhcGk6V2F1bXo5NHNjSA==',
		'Cookie': 'APPSESSIONID=39CA9453A74728BE5CB3DA6610829DC1; JSESSIONIDSSO=87978D01CEC651AEEA9AC3F05CAA6B42'
	}
	response = requests.request("DELETE", url, headers=headers, data=payload, verify=False)


def AccountList():
	email = '@obghk.ru'
	url = f"https://{config.ip}:9060/ers/config/internaluser/?filter=email.CONTAINS." + email
	payload = {}
	headers = {
		'Accept': 'application/json',
		'Content-Type': 'application/json',
		'Authorization': 'Basic Z29kb2ZhcGk6V2F1bXo5NHNjSA==',
		'Cookie': 'APPSESSIONID=39CA9453A74728BE5CB3DA6610829DC1; JSESSIONIDSSO=87978D01CEC651AEEA9AC3F05CAA6B42'
	}
	response = requests.request("GET", url, headers=headers, data=payload, verify=False)
	jsonData = response.text
	dictData = json.loads(jsonData)
	clear_data = dictData["SearchResult"]["resources"]
	return clear_data


@app.route('/', methods=["GET", "POST", "DELETE"])
def gfg():
	if 'user' in session:
		user_list = []
		for i in AccountList():
			user_list.append(f"{i['name']} - {i['description']}")
		flash(AccountCount())
		for _ in user_list:
			flash(_)
		if request.method == "POST":
			samaccountname = request.form.get("lname").lower()
			if request.form['submit_button'] == 'Create user':
				if AccountCount() < 100:
					period = request.form.get("period")
					if period == '':
						print(period)
					else:
						CreateISEUser(samaccountname, period)
				else:
					pass
		if request.method == "POST":
			samaccountname = request.form.get("lname").lower()
			if request.form['submit_button'] == 'Remove user':
				RemoveISEuser(samaccountname)
		return render_template('index.html')
	return redirect(url_for('login'))


@app.route('/login', methods=['POST', 'GET'])
def login():
	if 'user' in session:
		return redirect(url_for('gfg'))
	else:
		if request.method == "POST":
			username = request.form['username']
			password = request.form['password']
			user = [x for x in users if x.username == username][0]
			if user and user.password == password:
				session['user'] = user.username
				return redirect(url_for('gfg'))
	return render_template('login.html')


if __name__ == '__main__':
	users.append(User(username='obghk.admin', password=os.environ.get('obghk.admin')))
	app.run(debug=True, host='0.0.0.0', port='80')
