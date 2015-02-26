from __future__ import division

import re
import json
import time

try:
    import scrypt
except:
    print "Scrypt module missing, Scrypt support is disabled on this machine"


class Bunch(object):
    '''Create a BUNCH object that moves things in a dict into namespace'''
    def __init__(self, adict):
        self.__dict__.update(adict)


def configGen():
    '''Load a config from disk into memory and move it into namespace'''  # Rewrite this and the email loader to be cleaner (?)
    conf = 'config/config.json'
    try:
        with open('{}'.format(conf), 'r') as f:
            config = json.load(f)
    except:
        with open('../{}'.format(conf), 'r') as f:  # Second attempt to see if it's a folder up or not
            config = json.load(f)

    return Bunch(config)


class WebData(object):
    def __init__(self):
        pass

    def post(self, request, response, required):
        '''Read POST body data and verify it by a list of required fields'''
        try:
            post = json.load(request.body)  # Load the request body into json
            for item in required:  # Make sure the required fields are there
                if item not in post:
                    raise Exception  # Except out if they're missing
        except Exception as e:
            raise Exception('Request body was invalid missing, or a fragment')

        return Bunch(post)

    def email(self, filename):
        '''Load an email template from disk into memory'''
        try:
            with open('{}'.format('config/{}'.format(filename)), 'U') as f:
                return f.read()
        except:
            with open('{}'.format('../config/{}'.format(filename)), 'U') as f:  # Second attempt to see if it's a folder up or not
                return f.read()


class Iterate(object):
    def __init__(self):
        pass

    def send(self, data, mode=None):  # The mode flip allows me to pretty-print json data
        '''Export the data outputs into json'''
        if mode is None:
            return json.dumps(data)
        else:
            return json.dumps(data, sort_keys=True, indent=4)

    def validateEmail(self, email):
        '''Check to make sure the email address is valid'''
        if re.match(r".+@.+\.\w+", email):  # Using regex seriously sucks for this but it's the best option at the moment
            return True
        return False
