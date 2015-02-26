#!/bin/python

from __future__ import division, absolute_import, print_function

import json
import time
import base64
import argparse

from core import crypto


class Quikly(object):
    def __init__(self):
        pass

    def handler(self):
        message = "Hello World"
        return Tester().main(message)


class Tester(object):
    def __init__(self):
        self.QuiCrypt = crypto.QuiCrypt()

    def main(self, message):
        print("Generating Keypair and Secret")
        secret, priv, pub = self.generate()
        print("Starting the Encrypter")
        encrypted = self.encrypt(pub, secret, message)
        print("Handing off to the decrypter")
        message, secret = self.decrypt(priv, encrypted['key'], encrypted['message'])
        return("The decrypted message was '{}', secret was '{}'".format(message, secret))

    def generate(self, aeslen=128, rsalen=1024):
        print("Generating a Secret Key")
        secret = self.QuiCrypt.secretGenerator(aeslen)
        print("Generating the Key Pair")
        priv, pub = self.QuiCrypt.keyGenerator(rsalen)
        return secret, priv, pub

    def encrypt(self, pub, secret, message):
        print("Encrypting the Secret Key")
        package = self.QuiCrypt.encryptAES(secret, message)
        print("Encrypting the Message")
        secretkey = self.QuiCrypt.encryptRSA(pub, secret)
        return dict(key=secretkey, message=package)

    def decrypt(self, priv, secretkey, package):
        print("Decrypting the Secret Key")
        secret = self.QuiCrypt.decryptRSA(priv, secretkey)
        print("Decrypting the Message")
        message = self.QuiCrypt.decryptAES(secret, package)
        return message, secret


def run():
    parser = argparse.ArgumentParser(description='Quik \r\n A simple encrypted chat program')

    keys = parser.add_argument_group("Signing key Settings", "Options that allow you to chose what key you use among other things")
    keys.add_argument("-pr", "--private", dest="privkey", help="Location of the private key file", default="")
    keys.add_argument("-pu", "--public", dest="pubkey", help="Location of the public key file", default="")
    keys.add_argument("-ks", "--keystore", dest="keystore", help="Location of the key storage", default="")
    options = parser.parse_args()

    data = Quikly().handler()
    print(data)

run()
