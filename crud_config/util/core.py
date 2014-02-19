# Import classes from module
from ctkapi import Connector

class CoreAPI():

    def __init__(self,user,password,environment):
        self._user = user
        self._pass = password
        self._env = environment
        self.authenticate()

    def authenticate(self):
        """Authenticate the client if not authenticated"""
        if hasattr(self, "core_client"):
            return self.core_client
        try:
            self.core_client = Connector(self._env)
            self.core_client.auth(self._user,self._pass)
        except Exception as e:
            raise
            raise Exception("Unable to authenticate")
        return self.core_client

    def get_devices(self,device_ids):
        if not device_ids:
            return []
        attributes = ["name","number","account"]
        dict_query = {
            "class": "Computer.Computer",
            "load_arg": {
                "class": "Computer.ComputerWhere",
                "values": [
                    [ "number", "in", device_ids ],
                    ],
                "offset": 0
            },
            "attributes": attributes
        }
        query_result = self.core_client.query(dict_query)
        devices = query_result[0]['result']
        return devices

    def get_devices_for_account(self,account_ids,offset=0):
        if not account_ids:
            return []
        attributes = ["name","number","account","primary_ip","ip_addresses",
                      "os"]
        dict_query = {
            "class": "Computer.Computer",
            "load_arg": {
                "class": "Computer.ComputerWhere",
                "values": [
                    [ "account", "in", account_ids ],
                    ],
                "offset": offset
            },
            "attributes": attributes
        }
        query_result = self.core_client.query(dict_query)
        devices = query_result[0]['result']
        return devices

    def get_accounts(self,account_ids,offset=0):
        if account_ids:
            value = ["number", "in", account_ids]
        else:
            value = ["number", ">", "0"]
        attributes = ["number","name","device_count","company_subtype"]
        dict_query = {
            "class": "Account.Account",
            "load_arg": {
                "class": "Account.AccountWhere",
                "values": [value],
                "offset": offset
            },
            "attributes": attributes
        }
        try:
            query_result = self.core_client.query(dict_query)
            accounts = query_result[0]['result']
        except Exception:
            accounts = []
        return accounts