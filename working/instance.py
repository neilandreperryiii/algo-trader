import helper as h
import robin_stocks.robinhood as robin

class RobinhoodInstance: # robinhood instance
    def __init__(self):     # init
        self.credsPath = "creds/robinhood.json"
        self.status = 0
        self.loginToRobinhood()

    def loginToRobinhood(self): # login
        creds = h.getJsonLoad(self.credsPath)
        self.login = robin.login(creds["username"], creds["password"], mfa_code=self.getMfaCode(creds["auth_key"]))
