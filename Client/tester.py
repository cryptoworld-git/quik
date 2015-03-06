#!/bin/python

from __future__ import division, absolute_import, print_function

import json
import time
import base64
import scrypt
import urllib2
import argparse

from core import crypto


api_host = 'http://quik.dah.io/api/v1/'


class QuikError(Exception):
    pass


class Quikly(object):
    def __init__(self):
        pass

    def handler(self, options):
        utils = Utilities()
        crypt = crypto.QuiCrypt()
        randstr = crypt.secretGenerator

        user = {}

        if options.auth == "pass": method = 'password'
        if options.auth == "key": method = 'signature'

        if options.loaduser: 
            print("Loading user info from disk")
            user = json.loads(utils.disk("", options.loaduser, "read"))
            if 'clid' in user: options.clid = user['clid']
            if 'name' in user: options.name = user['name']
            if 'uuid' in user: options.uuid = user['uuid']
            if 'email' in user: options.email = user['email']
            if 'phrase' in user: options.phrase = user['phrase']
            if 'privkey' in user: options.private = user['privkey']
            if 'keypass' in user: options.keypass = user['keypass']

        if not options.phrase:
            return "a phassphrase is required if you do not load from file"

        if not options.uuid and not options.email: 
            return "an email address is required if you do not specify a uuid or load from file"

        if not options.uuid and not options.name:
            return "a username is required if you do not specify a uuid or load from file"

        if options.private:
            print("Loading private key from disk")
            private = utils.disk("", options.private, "read")
            private, public = crypt.keyLoader(private, options.keypass)
        else:
            print("Generating a new private key")
            private, public = crypt.keyGenerator(4096, options.keypass)

        if options.savekey: 
            utils.disk(private, options.savekey, "write")

        if not options.uuid: 
            print("No UUID found, registering for a new account")
            req_url = '{}account/user/auth/new'.format(api_host)
            phash = utils.scryptHash(options.phrase, randstr())
            response = utils.urlreq(req_url, dict(name=options.name, email=options.email, key=public, password=phash))
            user['uuid'] = json.loads(response)['uuid']
            options.uuid = user['uuid']

        if options.savepass:
            user['phrase'] = options.phrase

        if options.saveuser:
            print("Saving user info to file")
            if options.clid: user['clid'] = options.clid
            if options.uuid: user['uuid'] = options.uuid
            if options.name: user['name'] = options.name
            if options.email: user['email'] = options.email
            if options.savekey: user['privkey'] = options.savekey
            if options.keypass and options.savekey: user['keypass'] = options.keypass
            utils.disk(utils.jsonify(user, True), options.saveuser, "write")

        print("Requesting required inforomation to login")
        req_url = '{}account/user/auth/init'.format(api_host)
        response = utils.urlreq(req_url, dict(uuid=options.uuid, method=method))
        auth = json.loads(response)
        
        if 'salt' in auth:  # If the Quik server handed us a "SALT" field it means we're logging in with a PASSWORD
            print("Authenticating via password login")
            salt = auth['salt']
            if 'scrypt' in salt:  # Due to the flexibility on the Quik hashing methods, we check what method was used before
                phash = utils.scryptHash(options.phrase, *salt.lstrip('scrypt$').split('$'))  # Pull the variables like N, r, p, and len out for hash generation
                auth['hmac'] = crypt.hmacGenerator(phash[-34:-2], auth['login_session'])  # HMAC the last 32 characters of the hash with login session
            else:
                return "Only Scrypt is implimented"  # Scrypt is the default, we don't need to test anything else in this case
        else:  
            print("Authenticating via private key login")
            auth['signature'] = crypt.createSignature(private, auth['login_session'], options.keypass)  # Sign the login session with our private key

        req_url = '{}account/user/auth/login'.format(api_host)
        auth['client_uuid'] = options.clid
        return utils.urlreq(req_url, auth)





class Utilities(object):
    def __init__(self):
        pass

    def jsonify(self, data, pretty=False):
        if pretty is True:
            return json.dumps(data, sort_keys=True, indent=4)
        else:
            return json.dumps(data)

    def disk(self, data, location, mode):
        if mode is "read":
            with open(location, "U") as f:
                return f.read()
        elif mode is "write":
            with open(location, "w+") as f:
                f.seek(0)
                f.write(data)
                f.truncate()
                return

    def urlreq(self, url, data):
        '''Open a HTTP connection to a server'''
        try:
            req = urllib2.Request(url, json.dumps(data), {'Content-Type': 'application/json'})
            f = urllib2.urlopen(req)
            response = f.read()
            f.close()
            return response
        except urllib2.HTTPError, error:
            raise QuikError(error.read())

    def scryptHash(self, passwd, salt, N=32*1024, r=16, p=6, llen=256):
        '''Generate our Scrypt hash with flexible perameters and merge it with it's salt'''
        passwd = b'{}'.format(passwd)
        salt = b'{}'.format(salt)
        hashstr = base64.b64encode(scrypt.hash(passwd, str(salt), int(N), int(r), int(p), int(llen)))  # Perform the hashing with specified settings and b64 encode
        return "scrypt${}${}${}${}${}${}".format(salt, N, r, p, llen, hashstr)  # Merge the hash with the salt



def run():
    parser = argparse.ArgumentParser(description='Quik \r\n A simple encrypted chat program')

    keys = parser.add_argument_group("Signing key settings", "Options that allow you to chose what key you use among other things")
    keys.add_argument("--savekey", dest="savekey", help="Enable saving of the generated keys at location", default=False)
    keys.add_argument("--private", dest="private", help="Location of the private key", default=False)
    keys.add_argument("--keypass", dest="keypass", help="The password for the private key", default=None)

    user = parser.add_argument_group("User account settings", "Settings for the user account for authentification")
    user.add_argument("--saveuser", dest="saveuser", help="Enable saving of the generated user block at location", default=False)
    user.add_argument("--savepass", dest="savepass", help="Save the passphrase with the generated user block", default=False, action='store_true')
    user.add_argument("--loaduser", dest="loaduser", help="Destination for the user block that will fill in the defaults. Trumps other settings.", default=False)
    user.add_argument("--uuid", dest="uuid", help="The UUID you wish to login with", default=False)
    user.add_argument("--pass", dest="phrase", help="The passphrase for scrypt based login", default=False)
    user.add_argument("--name", dest="name", help="The username you wish to use with Quik", default=False)
    user.add_argument("--email", dest="email", help="The unique email address for use with Quik", default=False)

    login = parser.add_argument_group("Login configuration settings", "Settings that affects how you login")
    login.add_argument("--auth", choices=['pass', 'key'], help="The preferred authentification method", dest="auth", default="key")
    login.add_argument("--clid", help="Client UUID to be sent to the server", default="Quik-Default-Test-Client-Revision-01")

    options = parser.parse_args()

    data = Quikly().handler(options)
    print(data)

run()
