# Quik Communications API
This is the documentation for all of the API calls for the Quik API

Notes:
  - While most fields are capital here, they are actually to be requested in lowercase.
  - `status` is included with most replies from the server, if it is not `OK` you won't get all fields back
  - All requests are POST with the fields being keys in a JSON array
  - All of these API endpoints are subject to change as development progresses
  - Every client should have the server's parent RSA key embedded in it for true verification

---------------------------------------------------------------------------------------------------------
## Registration 

**Register**: *Client* -> *Auth Server* ~ http://quik.dah.io/api/v1/account/user/auth/new
```json
{
  "payload": 
    {
      "email": "", "name": "", "key": "", "password": ""
    }, 
  "signature": ""
} 
```
  - `email` Must be unique
  - `name` is your display name and will be displayed case sensitive
  - `key` is your public key
  - `password` is your complete password hash with salt headers, this is optional.
  - `signature` is a signature of `payload` generated with `key`  
 -> **Give Account**
  
  &nbsp;

**Give Account**: *Auth Server* -> *Client* ~ 
```json
{
  "status": "", 
  "payload": 
    {
      "verified": false, "name": "", "display": "", 
      "created": 100000.01, "email": "", "key": "", "uuid": ""
    }, 
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

