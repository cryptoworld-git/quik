# Quik Communications API
This is the documentation for all of the API calls for the Quik API

---------------------------------------------------------------------------------------------------------
## Notes
  - `status` is included with most replies from the server, if it is not `OK` you won't get all fields back
    - If `status` is not `OK` it will be a number referencing to a status message inluded in the reply
  - All requests are POST with the fields being keys in a JSON array unless stated otherwise
  - All of these API endpoints are subject to change as development progresses
  - Every client should have the server's parent RSA key embedded in it for true verification  
&nbsp;
  - All replies from the server will include a `verification` array containing `signature` and `uuid`
    - `signature` is the `payload` signed with all the keys sorted alphabetically
    - `uuid` is the uuid of the key it was signed with, this is for if the key is changed from the enbedded one
    - Updated keys can be requested from http://quik.dah.io/api/v1/systems/key/`uuid`
    - If the returned key isn't the parent key, it will be signed by the parent key for verification  
&nbsp;
  - All messages from the client must include both `signature` and `payload` keys
    - `signature` is the `payload` signed with all the keys sorted alphabetically
    - This is signed with the client's private key and must match the public shared with server  


---------------------------------------------------------------------------------------------------------
## Registration 

**Register**: POST *Client -> Auth Server* ~ http://quik.dah.io/api/v1/account/user/auth/new
```json
{
  "payload": 
    {"email": "", "name": "", "key": "", "password": ""}, 
  "signature": ""
} 
```
  - `email` Must be unique
  - `name` is your display name and will be displayed case sensitive
  - `key` is your public key
  - `password` is your complete password hash with salt headers, this is optional.  
 -> **Give Account**
  
  &nbsp;

**Give Account**: POST *Auth Server -> Client*
```json
{
  "status": "", 
  "payload": 
    {"verified": false, "name": "", "display": "", 
    "created": 100000.01, "email": "", "key": "", "uuid": ""}, 
  "verification": 
    {"signature": "", "uuid": ""}
}
```
  - This is essentially the users profile block as the payload
  - `uuid` is your newly generated UUID
  - `name` is a lowercase version of the `name` sent to the server
  - `display` is the properly cased version
  - `created` is the time that the account was created
  - `verified` is `false` by default and changes to `true` when email verification is complete  
 -> **NONE**

