#!/usr/bin/python

import ldap
import sys
from flask import Flask, jsonify, request
from flask_restful import Resource, Api


app = Flask(__name__)
api = Api(app)

#ldapserver = "10.200.3.10"

class tokenStatus(Resource):
	def post(self):

		username=request.form.get("username")
		server = "10.200.3.10"
		
		ldapurl = "ldap://" + server + ":389"
		l = ldap.initialize(ldapurl)
		binddn = "CN=Aplicativo RSS Brasil,OU=Sunray,OU=Usuarios Aplicativos,OU=Usuarios,OU=MELI,OU=MercadoLibre,DC=ml,DC=com"
		pw = "Md4!3_2JsWe$"
		basedn = "OU=MercadoLibre,dc=ml,dc=com"
		searchFilter = "sAMAccountName=" + username
		searchAttribute = ["lockoutTime"]
		searchScope = ldap.SCOPE_SUBTREE

		try:
			l.protocol_version = ldap.VERSION3
			l.simple_bind_s(binddn, pw)
		except ldap.INVALID_CREDENTIALS:
			return "Usuario o clave de AD incorrectos."
			sys.exit(0)
		except ldap.LDAPError, e:
			if type(e.message) == dict and e.message.has_key('desc'):
				return e.message['desc']
			else:
				return e
			sys.exit(0)
		try:
			ldap_result_id = l.search(basedn, searchScope, searchFilter, searchAttribute)
			result_set = []
			while 1:
				result_type, result_data = l.result(ldap_result_id, 0)
				if (result_data == []):
					break
				else:
					if result_type == ldap.RES_SEARCH_ENTRY:
						result_set.append(result_data)

					if len(result_set) == 0:
						return "No hubieron resultados."
					for i in range(len(result_set)):
						for entry in result_set[i]:
							try:
								lockedTime = entry[1]['lockoutTime'][0]
								if lockedTime == "0":
									active = "Activo"
									return active
								else:
									active = "Bloqueado"
									return active
							except:
								pass
		except ldap.LDAPError, e:
			return e
		l.unbind_s()

api.add_resource(tokenStatus, '/')

if __name__ =="__main__":
	app.run('127.0.0.1',5000,debug=True)
