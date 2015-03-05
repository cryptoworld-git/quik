
---------------------------------------------------------------------------------------------------------
## Login Requests 

**Login Req**: *Client* -> *Auth Server* ~ `UUID`, `METHOD`
    - *Client* sends `UUID`, `METHOD` to the *Auth Server*.
    - `METHOD` can be either `PASSWORD` or `SIGNATURE`
 -> **Login Spec**

**Login Spec**: *Auth Server* -> *Client* ~ `UUID`, `LOGIN_SESSION`, (`SALT`)
    - *Auth Server* sends `UUID`, `LOGIN_SESSION`
    - Optional field `SALT` is sent if previous `METHOD` was `PASSWORD`
 -> **Login Final**

**Login Final**: *Client* -> *Auth Server* ~ `UUID`, `LOGIN_SESSION`, `HMAC/SIGNATURE`
    - *Client* sends `UUID`, LOGIN_SESSION
    - HMAC is the last 32 digits password hash HMAC 512'd with LOGIN_SESSION
    - SIGNATURE is a signature of LOGIN_SESSION signed by the user's private key
 -> **Create Session**

**Create Session**: *Auth Server* -> *Client* ~ `UUID`, `CLIENT_SESSION`
    - *Auth Server* sends `UUID`, `CLIENT_SESSION`
    - `CLIENT_SESSION` is invalid until it's assigned a `CLIENT_UUID`
 -> **Validate Session**

---------------------------------------------------------------------------------------------------------
## Session Validation

**Validate Session**: *Client* -> *Session Server* ~ `UUID`, `CLIENT_SESSION`, `CLIENT_UUID`
    - *Client* sends `UUID`, `CLIENT_SESSION`, `CLIENT_UUID`
    - `CLIENT_UUID` is the `UUID` unique specifically to that device and client
 -> **Give TIME_KEY**

**Give TIME_KEY**: *Session Server* -> *Client* ~ `CLIENT_SESSION`, `TIME_KEY`
    - *Session Server* sends `CLIENT_SESSION`, `TIME_KEY` to *Client*
    - `TIME_KEY` is a token that is only valid for a certain amount of time
 -> **NONE**

---------------------------------------------------------------------------------------------------------
## Session Renewal

**Renew Session**: *Client* -> *Session Server* ~ `UUID`, `CLIENT_SESSION`, `CLIENT_UUID`, (`TIME_KEY`)
    - *Client* sends `UUID`, `CLIENT_SESSION`, `CLIENT_UUID` to *Session Server*
    - `TIME_KEY` is included when the client had a previous `TIME_KEY`
 -> **Renewed Session**

**Renewed Session**: *Session Server* -> *Client* ~ `STATUS`, (`TIME_KEY`, `CLIENT_SESSION`)
    - *Session Server* sends `STATUS`, `TIME_KEY`
    - `CLIENT_SESSION` is regenerated as STALE
    - `STATUS` can be `OK`, `FAIL`, or `ROTTEN`
        - `OK` means session sucessfully renewed 
        - `FAIL` means `CLIENT_SESSION` or `CLIENT_UUID`, or `UUID` were invalid
        - `ROTTEN` means that `CLIENT_SESSION` had been marked `STALE` too many times (100) or was too old 
            - *Client* has to login again
 -> **NONE**

---------------------------------------------------------------------------------------------------------
## Session Invalidation

**Remove Session**: *Client* -> *Session Server* ~ `UUID`, `CLIENT_SESSION`, `CLIENT_UUID`, (`TIME_KEY`)
    - *Client* sends `UUID`, `CLIENT_SESSION`, `CLIENT_UUID` to *Session Server*
    - `TIME_KEY` is included when the client had a previous `TIME_KEY`
 -> **Sessions Removed**

**Sessions Removed**: *Session Server* -> *Client* ~ `STATUS`
    - *Session Server* sends `STATUS` to *Client*
    - `STATUS` can be `OK`, `FAIL`, or STALE
        - `OK` means all `CLIENT_SESSION`'s and `TIME_KEY`'s were invalidated
        - `FAIL` means `CLIENT_SESSION` or `CLIENT_UUID`, or `UUID` were invalid
        - `STALE` means `CLIENT_SESSION` was `STALE` 
            - *Client* has to login again to perform this action
 -> **NONE**

---------------------------------------------------------------------------------------------------------
## Message Send / Request

**Send Message**: *Client* -> *Relay Server* ~ `UUID`, `CLIENT_UUID`, MESSAGE_PAYLOAD, `TIME_KEY`
    - *Client* sends `UUID`, CLIENT_UU*ID, MESSAGE_*PAYLOAD, `TIME_KEY` to Relay Server
    - MESSAGE_PAYLOAD is a nested array of items
    - `TIME_KEY` is the key from the *Session Server*
 -> **Validate *Client***

**Get Message**: *Client* -> *Relay Server* ~ `UUID`, `CLIENT_UUID`, `TIME_KEY`, (SIZE)
    - *Client* sends `UUID`, `CLIENT_UUID`, `TIME_KEY` to *Relay Server*
    - SIZE is an optional field for a specific number of messages, default 25
 -> **Validate *Client***

**Get New**: *Client* -> *Relay Server* ~ `UUID`, `CLIENT_UUID`, `TIME_KEY`
    - *Client* sends *UUID, `CLIENT_UUID`, `TIME_KEY` to Relay Server
 -> **Validate Client**

---------------------------------------------------------------------------------------------------------
## Client Validation

**Validate Client**: *Relay Server* -> *Session Server* ~ `TIME_KEY`, `CLIENT_UUID`
    - *Relay Server* sends `UUID`, `TIME_KEY`, `CLIENT_UUID` to *Session Server*
    - `UUID` is the user's `UUID`
 -> **Approve Client**

**Approve *Client***: *Session Server* -> *Relay Server* ~ `STATUS`
    - *Session Server* sends STATUS to *Relay Server*
    - `STATUS` can either be EXPIRED, `OK`, `FAIL`
        - `OK` is when all things pass
        - `FAIL` is when `UUID` and `CLIENT_UUID` do not match
        - `EXPIRED` is when `TIME_KEY` is invalid but everything else matches
 -> **Relay Response**

**Relay Response**: *Relay Server* -> *Client* ~ `STATUS`, (`PAYLOAD`)
    - *Relay Server* sends `STATUS` to *Client*
    - `STATUS` can be the same replies as Approve *Client*'s `STATUS` 
    - `PAYLOAD` is included when client requested messages, it is a nested array
 -> **NONE**
