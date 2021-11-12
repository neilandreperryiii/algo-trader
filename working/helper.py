import json
import pyotp

def getJsonLoad(fileName): # get json loads
    with open(fileName) as f:
        data = json.load(f)
    return data

def getMfaCode(authKey): # get current mfa code
    return pyotp.TOTP(authKey).now()