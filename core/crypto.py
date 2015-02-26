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
        '''Generate a HMAC of two items using SHA512 by default, and return it in hex'''
        secret = b"{}".format(secret)  # Ensure they're in BINARY format
        message = b"{}".format(message)
        h = HMAC.new(secret, digestmod=digest)  # Create the HMAC base
        h.update(message)  # Add our message to the HMAC
        return h.hexdigest()  # Return the HMAC

    def keyGenerator(self, bits=8192, passwd=None):
        '''Generate a new key based on bitlength, and optionally encrypt it if password is present'''
        print("Generating a {} bit length key, this might take a minute".format(bits))
        keypair = RSA.generate(bits)  # Actually generate the keypair
        if passwd is None:
            privkey = keypair.exportKey("PEM")  # Don't encrypt it if no password is specified and export it
        else:
            privkey = keypair.exportKey("PEM", passphrase=passwd)  # Encrypt the private key and export it
        pubkey = keypair.publickey().exportKey("OpenSSH")  # Export the public key in OpenSSH format 
        return privkey, pubkey

    def secretGenerator(self, chars=32):
        '''Gererate a completely random 32 byte secret key'''
        secret = random.getrandbits(((chars*8)+8))  # We get our length in BYTES not bits, but we generate in BITS length
        secret = base64.b64encode("{}".format(secret))[:chars]  # Make sure we really don't get too many bits and encode in base64 (REMOVE B64?)
        return secret

    def encryptRSA(self, public, message):
        '''Encrypt a string of data with a RSA Public Key'''
        pub = RSA.importKey(public)  # Import the Public Key
        enc = PKCS1_OAEP.new(pub)  # Create a new encryption object with the public key
        enc = enc.encrypt(message)  # Encrypt the message
        return enc.encode('base64')  # Return the message encded in base64

    def decryptRSA(self, private, package, passwd=None):
        '''Decrypt a encrypted message with the matching RSA Private Key'''
        priv = RSA.importKey(private, passphrase=passwd)  # Import the Private Key, optionally with password if it's encrypted
        enc = PKCS1_OAEP.new(priv)  # Create a new decryption object with the private key
        package = base64.b64decode(package)  # Decode the message from base64
        enc = enc.decrypt(package)  # Actually decrypt the message
        return enc

    def createSignature(self, private, message, passwd=None):
        '''Sign a string of data with a RSA Prviate key'''
        rsakey = RSA.importKey(private, passphrase=passwd)  # Import the private key, optionally with password if it's encrypted
        signer = PKCS1_v1_5.new(rsakey)  # Create a new signer object with the private key
        digest = SHA256.new()  # Set it to use SHA256 for the signature
        digest.update(message)  # Add the message to the object
        sign = base64.b64encode(signer.sign(digest))  # Sign the message and encode it in base64
        return sign

    def checkSignature(self, public, signature, message):
        '''Verify a signed message with the matching RSA Publick Key'''
        rsakey = RSA.importKey(public)  # Import the public key
        signer = PKCS1_v1_5.new(rsakey)  # Create a new signer object for the public key
        digest = SHA256.new()  # Set it to use SHA256 for the signature
        digest.update(message)  # Add the message to the object
        if signer.verify(digest, base64.b64decode(signature)):  # Verify the object with the message against the signature we recieved
            return True
        return False

    def encryptAES(self, secret, message):
        '''Encrypt and Pad a message in AES with a Secret Key'''
        padded = pad(message)  # Pad our message to ensure it's proper length
        iv = Random.new().read(AES.block_size)  # Generate a new IV based on block size
        cipher = AES.new(secret, AES.MODE_CBC, iv)  # Create a new AES encryption object using our secret key and our IV, set mode to CBC
        return base64.b64encode(iv + cipher.encrypt(padded))  # Encrypt the message itself and add the IV to it then base64 encode it

    def decryptAES(self, secret, package):
        '''Decrypt a padded message in AES with a Secret Key'''
        package = base64.b64decode(package)  # Decode our message from base64
        iv = package[:16]  # Strip out our IV because we already know the length (Block Size)
        cipher = AES.new(secret, AES.MODE_CBC, iv)  # Create a new AES encryption object sing our secret key and our IV, set mode to CBC
        return unpad(cipher.decrypt(package[16:]))  # Decrypt the encrypted string we recieved after trimming out the first 16 characters of IV
