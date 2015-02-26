from __future__ import division, absolute_import, print_function

import json
import time
import base64

try:
    from Crypto import Random
    from Crypto.Hash import SHA, SHA256, SHA512, HMAC
    from Crypto.Cipher import AES
    from Crypto.Cipher import PKCS1_OAEP
    from Crypto.Random import random
    from Crypto.PublicKey import RSA
    from Crypto.Signature import PKCS1_v1_5
except:
    raise ImportError("It appears the PyCrypto module is missing or installed incorrectly, make sure it is installed and uses the correct case")

pad = lambda s: s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)
unpad = lambda s: s[:-ord(s[len(s)-1:])]


class QuiCrypt(object):
    def __init__(self):
        pass

    def hmacGenerator(self, secret, message, digest=SHA512):
        secret = b"{}".format(secret)
        message = b"{}".format(message)
        h = HMAC.new(secret, digestmod=digest)
        h.update(message)
        return h.hexdigest()

    def keyGenerator(self, bits=8192, passwd=None):
        '''Generate a new key based on bitlength, and optionally encrypt it if password is present'''
        print("Generating a {} bit length key, this might take a minute".format(bits))
        keypair = RSA.generate(bits)
        if passwd is None:
            privkey = keypair.exportKey("PEM")
        else:
            privkey = keypair.exportKey("PEM", passphrase=passwd)
        pubkey = keypair.publickey().exportKey("OpenSSH")
        return privkey, pubkey

    def secretGenerator(self, chars=32):
        '''Gererate a completely random 32 byte secret key'''
        secret = random.getrandbits(((chars*8)+8))
        secret = base64.b64encode("{}".format(secret))[:chars]
        return secret

    def encryptRSA(self, public, message):
        '''Encrypt a string of data with a RSA Public Key'''
        pub = RSA.importKey(public)
        enc = PKCS1_OAEP.new(pub)
        enc = enc.encrypt(message)
        return enc.encode('base64')

    def decryptRSA(self, private, package, passwd=None):
        '''Decrypt a encrypted message with the matching RSA Private Key'''
        priv = RSA.importKey(private, passphrase=passwd)
        enc = PKCS1_OAEP.new(priv)
        package = base64.b64decode(package)
        enc = enc.decrypt(package)
        return enc

    def createSignature(self, private, message, passwd=None):
        '''Sign a string of data with a RSA Prviate key'''
        rsakey = RSA.importKey(private, passphrase=passwd)
        signer = PKCS1_v1_5.new(rsakey)
        digest = SHA256.new()
        digest.update(message)
        sign = base64.b64encode(signer.sign(digest))
        return sign

    def checkSignature(self, public, signature, message):
        '''Verify a signed message with the matching RSA Publick Key'''
        rsakey = RSA.importKey(public)
        signer = PKCS1_v1_5.new(rsakey)
        digest = SHA256.new()
        digest.update(message)
        if signer.verify(digest, base64.b64decode(signature)):
            return True
        return False

    def encryptAES(self, secret, message):
        '''Encrypt and Pad a message in AES with a Secret Key'''
        padded = pad(message)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(secret, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(padded))

    def decryptAES(self, secret, package):
        '''Decrypt a padded message in AES with a Secret Key'''
        package = base64.b64decode(package)
        iv = package[:16]
        cipher = AES.new(secret, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(package[16:]))
