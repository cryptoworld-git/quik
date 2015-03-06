Notes:
  - While most fields are capital here, they are actually to be requested in lowercase.
  - `STATUS` is included with most replies from the server, if it is not `OK` you won't get all fields back
  - All requests are POST with the fields being keys in a JSON array
  - All of these API endpoints are subject to change as development progresses

---------------------------------------------------------------------------------------------------------
## Registration 

**Register**: *Client* -> *Auth Server* ~ `EMAIL`, `NAME`, `KEY`, (`PASSWORD`) | http://quik.dah.io/api/v1/account/user/auth/new
  - *Client* sends `EMAIL`, `NAME`, `KEY`, `PASSWORD` to *Auth Server*
  - `EMAIL` Must be unique
  - `NAME` is your display name and will be displayed case sensitive
  - `KEY` is your public key
  - `PASSWORD` is your complete password hash with salt headers  
 -> **Give Account**
  
  &nbsp;
  
**Give Account**: *Auth Server* -> *Client* ~ `STATUS`, `VERIFIED`, `NAME`, `DISPLAY`, `CREATED`, `EMAIL`, `KEY`, `UUID`
  - *Auth Server* sends `STATUS`, `VERIFIED`, `NAME`, `DISPLAY`, `CREATED`, `EMAIL`, `KEY`, `UUID` to *Client*
  - This is essentially the users profile block with the addition of the `STATUS` field
  - `UUID` is your newly generated UUID
  - `NAME` is a lowercase version of the `NAME` sent to the server
  - `DISPLAY` is the properly cased version
  - `CREATED` is the time that the account was created
  - `VERIFIED` is `FALSE` by default and changes to `TRUE` when email verification is complete  
 -> **NONE**

---------------------------------------------------------------------------------------------------------
## Login Requests 
  
**Login Req**: *Client* -> *Auth Server* ~ `UUID`, `METHOD` | http://quik.dah.io/api/v1/account/user/auth/init
  - *Client* sends `UUID`, `METHOD` to *Auth Server*.
  - `METHOD` can be either `PASSWORD` or `SIGNATURE`  
 -> **Login Spec**
  
  &nbsp;

**Login Spec**: *Auth Server* -> *Client* ~ `UUID`,  `STATUS`, `LOGIN_SESSION`, (`SALT`)
  - *Auth Server* sends `UUID`, `LOGIN_SESSION` to *Client* 
  - Optional field `SALT` is sent if previous `METHOD` was `PASSWORD`  
  - `STATUS` can be `OK` or `ERRCODE`
    - `ERRCODE` is actually a number. A field that's a number with the actual message will be included  
 -> **Login Final**
  
  &nbsp;
  
**Login Final**: *Client* -> *Auth Server* ~ `UUID`, `LOGIN_SESSION`, `CLIENT_UUID`, `HMAC/SIGNATURE` | http://quik.dah.io/api/v1/account/user/auth/login
  - *Client* sends `UUID`, `LOGIN_SESSION` to *Auth Server* 
  - `HMAC` is the last 32 digits password hash `HMAC` 512'd with `LOGIN_SESSION`
  - `CLIENT_UUID` is the `UUID` unique specifically to that device and client
  - `SIGNATURE` is a signature of `LOGIN_SESSION` signed by the user's private key  
 -> **Create Session**
  
  &nbsp;
  
**Create Session**: *Auth Server* -> *Client* ~ `UUID`, `STATUS`, `CLIENT_SESSION`
  - *Auth Server* sends `UUID`, `STATUS`, `CLIENT_SESSION` to *Client*
  - `CLIENT_SESSION` is invalid until it's assigned a `CLIENT_UUID`
  - `STATUS` can be `OK` or `ERRCODE`
    - `ERRCODE` is actually a number. A field that's a number with the actual message will be included  
 -> **Validate Session**

---------------------------------------------------------------------------------------------------------
## Session Validation and Renewal
  
**Validate Session**: *Client* -> *Session Server* ~ `UUID`, `CLIENT_SESSION`, `CLIENT_UUID`
  - *Client* sends `UUID`, `CLIENT_SESSION`, `CLIENT_UUID` to *Session Server*
  - `CLIENT_UUID` is the `UUID` unique specifically to that device and client  
 -> **Renewed Session**
  
  &nbsp;
  
**Renewed Session**: *Session Server* -> *Client* ~ `STATUS`, `IDENT`, `CLIENT_SESSION`
  - *Session Server* sends `STATUS`, `IDENT` to *Client*
  - `CLIENT_SESSION` is regenerated as `STALE`
  - `STATUS` can be `OK`, `ERRCODE`, or `ROTTEN`
    - `OK` means session sucessfully renewed
    - `ERRCODE` is actually a number. A field that's a number with the actual message will be included
    - `ROTTEN` means that `CLIENT_SESSION` had been marked `STALE` too many times (100) or was too old
      - *Client* has to login again  
 -> **NONE**

---------------------------------------------------------------------------------------------------------
## Session Invalidation
  
**Remove Session**: *Client* -> *Session Server* ~ `UUID`, `CLIENT_SESSION`, `CLIENT_UUID`, (`IDENT`)
  - *Client* sends `UUID`, `CLIENT_SESSION`, `CLIENT_UUID` to *Session Server*
  - `IDENT` is included when the client had a previous `IDENT`  
 -> **Sessions Removed**
  
  &nbsp;
  
**Sessions Removed**: *Session Server* -> *Client* ~ `STATUS`
  - *Session Server* sends `STATUS` to *Client*
  - `STATUS` can be `OK`, `ERRCODE`, or `STALE`
    - `OK` means all `CLIENT_SESSION`'s and `IDENT`'s were invalidated
    - `ERRCODE` is actually a number. A field that's a number with the actual message will be included
    - `STALE` means `CLIENT_SESSION` was `STALE`
      - *Client* has to login again to perform this action  
 -> **NONE**

---------------------------------------------------------------------------------------------------------
## Message Send / Request
  
**Send Message**: *Client* -> *Relay Server* ~ `UUID`, `CLIENT_UUID`, `MESSAGE_PAYLOAD`, `IDENT`
  - *Client* sends `UUID`, `CLIENT_UUID`, `MESSAGE_PAYLOAD`, `IDENT` to *Relay Server*
  - `MESSAGE_PAYLOAD` is a nested array of items
  - `IDENT` is the key from the *Session Server*  
 -> **Validate Client**
  
  &nbsp;
  
**Get Message**: *Client* -> *Relay Server* ~ `UUID`, `CLIENT_UUID`, `IDENT`, (`SIZE`)
  - *Client* sends `UUID`, `CLIENT_UUID`, `IDENT` to *Relay Server*
  - `SIZE` is an optional field for a specific number of messages, default 25  
 -> **Validate Client**
  
  &nbsp;
  
**Get New**: *Client* -> *Relay Server* ~ `UUID`, `CLIENT_UUID`, `IDENT`
  - *Client* sends `UUID`, `CLIENT_UUID`, `IDENT` to *Relay Server*  
 -> **Verify Client**

---------------------------------------------------------------------------------------------------------
## Client Verification
  
**Verify Client**: *Relay Server* -> *Session Server* ~ `UUID`, `IDENT`, `CLIENT_UUID`, `RELAY_UUID`
  - *Relay Server* sends `UUID`, `IDENT`, `CLIENT_UUID` to *Session Server*
  - `RELAY_UUID` is the UUID specific to that relay server
  - `UUID` is the user's `UUID`  
 -> **Approve Client**
  
  &nbsp;
  
**Approve Client**: *Session Server* -> *Relay Server* ~ `STATUS`
  - *Session Server* sends `STATUS` to *Relay Server*
  - `STATUS` can either be `OK`, `ERRCODE`, `EXPIRED`
    - `OK` is when all things pass
    - `ERRCODE` is actually a number. A field that's a number with the actual message will be included
    - `EXPIRED` is when `IDENT` is invalid but everything else matches  
 -> **Relay Response**
  
  &nbsp;
  
**Relay Response**: *Relay Server* -> *Client* ~ `STATUS`, (`PAYLOAD`)
  - *Relay Server* sends `STATUS` to *Client*
  - `STATUS` can be the same replies as **Approve Client**'s `STATUS`
  - `PAYLOAD` is included when client requested messages, it is a nested array  
 -> **NONE**
