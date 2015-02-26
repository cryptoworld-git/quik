# Quik Application Repo

## Quik API Information

### Hub


### Relay


### Client


## Quik Standards

### Client Standards

#### Chat Modes

Quik clients should support multiple chat modes. Chats in themselves may be able to house multiple different chat modes. This means that users are able to swap modes on the fly, able 
to change inbetween each individual message and does not require that the other party uses the same mode of communication. 

Different communication modes should be easy to spot when looking at actual messages. There should be a clear difference. 
    For example, each chat mode can have a particular background colour for the specific message. 

##### Client to Client

**Standard** - *Default* - Encrypted End-to-End - Fully encrypted messages between clients, encrypted over the wire, while in databases, and in memory. Complete and total encryption 
between both users. Every message should be encrypted with it's own random AES key and then the AEs key encrypted via the RSA Public Key of the recipient. 

**OTR** - *Optional* - Encrypted End-to-End without relay servers - This requires negotiation between the clients via the relay servers to establish a OTR connection directly between 
the two or more clients. This is similar to DSS in IRC chat. Due to the nature of this connection, if you lose internet connection you'll be disconnected and have to re-negotiate your 
connection to the other client. In some cases this may be difficult or impossible to use due to local firewall or NAT settings. 

**Unencrypted** - *Optional* - No Encryption at all - While this is not suggested, it should be a feature avaliable to users who do not care at all about encryption or may be 
experiencing issues with encryption on their devices. This just sends the message completely as plaintext. It will however be encrypted upon being recieved by the client when it is 
stored into the local device database. 

##### Client to Group extra modes

Client to Group modes are optional modes that exist in addition to the Client to Client modes 

**Shared Key** - *Default* - Transit and Resting State Encryption - This mode replaces "Standard" Client to Client encryption. Due to the amount of difficulty that a client might have 
encrypting the same message over and over again for different clients in the same group chat, this establishes that it should use the same key between the group. While each message 
will be encrypted with it's own random key, each client will recieve the message encrypted with the same AES key. The AES key will still be encrypted with each clients RSA Public Key.  

**Pre-Shared key** - *Optional* - Shared Key and Shared Encryption Key - this mode is a slightly weaker version of the "Shared key" option, and also replaces "Standard" Client to 
Client encryption. Due to the difficulty in encrypting a message key for multiple clients. This asks the server to generate a RSA key for the entire group, and hands the public key to 
the clients. This means when the message is encrypted, The AES key will be shared like "Shared Key" but the RSA key will be the one generated for the entire group, offloading all of 
the work to the Relay Server. The Relay Server will then be responsible to decrypt the AES key but not the message itself, and re-encrypt it for each member of the group using their 
personal RSA public keys. 

**Extra Encryption** - *Optional* - Full End-to-End Encryption - This mode replicates the "Standard" Client to Client encryption. This may be very taxing for your device and require a 
lot of memory and cpu power for larger groups. Each message will be encrypted with it's own random AES key for each member of the group, and use their personal RSA Public Key to 
encrypt the AES key. 

#### Memory and Storage

Everything kept in memory should be encrypted to prevent memory dump issues. 
Obviously, things currently displayed to the user will not be encrypted, but all other memory should be. 

Storage should be a flatfile local to the device that holds the last 500 messages. 
Messages saved to the device should be fully encrypted at all times. 
Optionally, Messages may be re-keyed on the device to share the same master key in order to speed up decryption times.

When the device locks, all memory of the current messages should be wiped out and the database completely unloaded. 
When user is inactive for more than 10 minutes, messages that aren't currently displayed on the screen should be cleared from memory and the database unloaded. 

#### Encryption and Hashing Methods

Quik is built to be very flexible when it comes to encryption, allowing you to pick what methods you'd like to use. 
Obviously this will raise compatibility issues if the reciving client does not allow the algorythm you've encrypted with. 
For this reason, there is a preferred encryption type that all clients *must* support under any circumstance. 

##### AES-CBC
    
Quik uses AES-CBC as it's standard for encrypting messages and files. 
The AES implimentation in Quik clients requires 256bit key length compatibility. 
This means if you only support 128bit or 192bit keys you don't meet the Quik Standard for AES

##### Scrypt 

Quik uses Scrypt as it's standard for hashing passwords, if passwords are used. 
The Scrypt implimentation in Quik clients requires the ability to set N, r, p, and length.

While you are able to set your own defaults for creation of new passwords, ensure that the N, r, p, and length variables can be changed.
You'll be informed of the N, r, p, and length values by the server when you're handed the salt for the user.

Scrypt has a heavy memory requirement, so when setting your clients default N, and r values, keep in mind other devices.
Devices such as Android phones that aren't current generation might have a restriction on memory limits.
It is suggested to ensure that your particular choice of Scrypt default should be 32mb of memory.

##### RSA 

Quik uses RSA as it's method for signatures and AES-Key encryption
Typically, RSA keys of 4096bits in length are to be used and are the minimum requirement. 
While it is unlikely to be an issue, greater length keys are also possible, such as 8192bit length keys. 

##### HMAC + SHA512

Quik uses HMAC with SHA512 for login authentification in some cases. This is likely when you choose to login via passwords. 
This means your client needs to support HMAC and SHA512 hashing. 


