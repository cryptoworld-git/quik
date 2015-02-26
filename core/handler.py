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
    conf = 'config/config.json'
    try:
        with open('{}'.format(conf), 'r') as f:
            config = json.load(f)
    except:
        with open('../{}'.format(conf), 'r') as f:
            config = json.load(f)

    return Bunch(config)


class WebData(object):
    def __init__(self):
        pass

    def post(self, request, response, required):
        '''Read POST body data and verify it by a list of required fields'''
        try:
            post = json.load(request.body)
            for item in required:
                if item not in post:
                    raise Exception
        except Exception as e:
            raise Exception('Request body was invalid missing, or a fragment')

        return Bunch(post)

    def email(self, filename):
        try:
            with open('{}'.format('config/{}'.format(filename)), 'U') as f:
                return f.read()
        except:
            with open('{}'.format('../config/{}'.format(filename)), 'U') as f:
                return f.read()


class Iterate(object):
    def __init__(self):
        pass

    def send(self, data, mode=None):
        '''Export the data outputs into json'''
        if mode is None:
            return json.dumps(data)
        else:
            return json.dumps(data, sort_keys=True, indent=4)

    def validateEmail(self, email):
        '''Check to make sure the email address is valid'''
        if re.match(r".+@.+\.\w+", email):
            return True
        return False
