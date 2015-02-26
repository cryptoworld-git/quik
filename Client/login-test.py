import scrypt
import json
import base64
import urllib2
from core import crypto

#uuid = 'c5f7ec55-a558-482a-9583-39d4ec852ecf'
keyfile = 'config/id_rsa'

quicrypt = crypto.QuiCrypt()
randstr = quicrypt.secretGenerator

api_host = 'http://dah.io:9818'


class QuikError(Exception):
    pass


def scryptHash(passwd, salt=randstr(), N=32*1024, r=16, p=6, llen=256):
    print "Salt: {}, N: {}, r: {}, p: {}, length: {}".format(salt, int(N), int(r), int(p), int(llen))
    hashstr = base64.b64encode(scrypt.hash(passwd, str(salt), int(N), int(r), int(p), int(llen)))
    return "scrypt${}${}${}${}${}${}".format(salt, N, r, p, llen, hashstr)


def urlreq(url, data):
    try:
        req = urllib2.Request(url, json.dumps(data), {'Content-Type': 'application/json'})
        f = urllib2.urlopen(req)
        response = f.read()
        f.close()
        return response
    except urllib2.HTTPError, error:
        raise QuikError(error.read())


def registerQuik(name, email, pubkey, hashstr):
    print "Registering for the Quik Service with the username {} and email {}".format(name, email)
    data = dict(name=name, email=email, key=pubkey, password=hashstr)
    return json.loads(urlreq('{}/user/new'.format(api_host), data))['id']


def authQuik(uuid, method='signature'):
    data = dict(id=uuid, method=method)
    response = urlreq('{}/user/authenticate'.format(api_host), data)
    return json.loads(response)


def loginQuik(uuid, auth, passwd=None, privkey=None):
    if 'salt' in auth:
        salt = auth['salt']
        if 'scrypt' in salt:
            salt = salt.lstrip('scrypt$')
            hashstr = scryptHash(passwd, *salt.split('$'))
            auth['hmac'] = quicrypt.hmacGenerator(hashstr[-34:-2], auth['login_session'])
        else:
            return "Only Scrypt is implimented"
    else:
        auth['signature'] = quicrypt.createSignature(privkey, auth['login_session'], passwd)

    return urlreq('{}/user/login'.format(api_host), auth)


#print scryptHash(passphrase)
#passphrase = raw_input("Your Quik Password >")
email = 'ksaredfx+testing@gmail.com'
passphrase = 'meow'
privkey, pubkey = quicrypt.keyGenerator(4096, passphrase)
hashstr = scryptHash(passphrase)
uuid = registerQuik('KsaRedFx', email, pubkey, hashstr)
print "Login {} with password status: {}".format(email, loginQuik(uuid, authQuik(uuid, 'password'), passphrase))
print "Login {} with signature status: {}".format(email, loginQuik(uuid, authQuik(uuid, 'signature'), passphrase, privkey))

