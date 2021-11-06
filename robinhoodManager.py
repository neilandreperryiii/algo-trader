
import robin_stocks.robinhood as robin

class RobinhoodInstance(): # robinhood instance
    def __init__(self): # init
        self.loginToRobinhood()

    def loginToRobinhood(self): # login
        creds = self.getCredentials
        self.login = robin.login(creds["username"], creds["password"], mfa_code=self.getMfaCode(creds["auth_key"]))

    def getCredentials(self): # get robinhood login credentials
        file_name = "creds/robinhood.json"
        with open(file_name) as f:
            data = json.load(f)
        return data

    def getMfaCode(self, var): # get current auth code
        return pyotp.TOTP(var).now()






p1 = RobinhoodManager()
p1