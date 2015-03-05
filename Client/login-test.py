import scrypt
import json
import base64
import urllib2
from core import crypto

#uuid = 'c5f7ec55-a558-482a-9583-39d4ec852ecf'
keyfile = 'config/id_rsa'

quicrypt = crypto.QuiCrypt()
randstr = quicrypt.secretGenerator

api_host = 'http://quik.dah.io/api/v1/'


class QuikError(Exception):
    pass


def scryptHash(passwd, salt=randstr(), N=32*1024, r=16, p=6, llen=256):
    '''Generate our Scrypt hash with flexible perameters and merge it with it's salt'''
    print "Salt: {}, N: {}, r: {}, p: {}, length: {}".format(salt, int(N), int(r), int(p), int(llen))  # Print off the specified settings
    hashstr = base64.b64encode(scrypt.hash(passwd, str(salt), int(N), int(r), int(p), int(llen)))  # Perform the hashing with specified settings and b64 encode
    return "scrypt${}${}${}${}${}${}".format(salt, N, r, p, llen, hashstr)  # Merge the hash with the salt


def urlreq(url, data):
    '''Open a HTTP connection to a server'''
    try:
        req = urllib2.Request(url, json.dumps(data), {'Content-Type': 'application/json'})
        f = urllib2.urlopen(req)
        response = f.read()
        f.close()
        return response
    except urllib2.HTTPError, error:
        raise QuikError(error.read())


def registerQuik(name, email, pubkey, hashstr):
    '''Register a new user account with Quik'''
    req_url = '{}account/user/auth/new'.format(api_host)
    print "Registering for Quik using the url {} with the username {} and email {}".format(req_url, name, email)
    data = dict(name=name, email=email, key=pubkey, password=hashstr)  # Pass USERNAME, EMAIL, PUBLIC KEY, and the hashed password + salt
    response = urlreq(req_url, data)
    return json.loads(response)['id']


def authQuik(uuid, method='signature'):
    '''Perform step number one of authentification with the Quik servers'''
    data = dict(id=uuid, method=method)
    req_url = '{}account/user/auth/init'.format(api_host)
    response = urlreq(req_url, data)  # All we have to do is fetch the login information like a token and salt
    return json.loads(response)


def loginQuik(uuid, auth, passwd=None, privkey=None):
    '''Perform step number two of authentification with the Quik servers'''
    if 'salt' in auth:  # If the Quik server handed us a "SALT" field it means we're logging in with a PASSWORD
        salt = auth['salt']
        if 'scrypt' in salt:  # Due to the flexibility on the Quik hashing methods, we check what method was used before
            salt = salt.lstrip('scrypt$')  # Strip out the method name
            hashstr = scryptHash(passwd, *salt.split('$'))  # Pull the variables like N, r, p, and length out of the rest of the salt and create our hash
            auth['hmac'] = quicrypt.hmacGenerator(hashstr[-34:-2], auth['login_session'])  # HMAC the last 32 characters of the hash with login session
        else:
            return "Only Scrypt is implimented"  # Scrypt is the default, we don't need to test anything else in this case
    else:  
        auth['signature'] = quicrypt.createSignature(privkey, auth['login_session'], passwd)  # Sign the login session with our private key

    req_url = '{}account/user/auth/login'.format(api_host)
    return urlreq(req_url, auth)  # Send the finished authentification to the server and get the reply



email = 'ksaredfx+secondary@gmail.com'
passphrase = 'meow'
privkey, pubkey = quicrypt.keyGenerator(4096, passphrase)

hashstr = scryptHash(passphrase)  # Generate our hash for registration
uuid = registerQuik('KsaRedFx', email, pubkey, hashstr)  # Pass varaibles and register

print "Login {} with password status: {}".format(email, loginQuik(uuid, authQuik(uuid, 'password'), passphrase))  # Test login via PASSWORD
print "Login {} with signature status: {}".format(email, loginQuik(uuid, authQuik(uuid, 'signature'), passphrase, privkey))  # Test login via RSA SIGNATURE
