#!/usr/bin/env python

import sys
import requests
import core
import time

import simplejson as json
from config import *

def main():
    headers = { "X-API-Auth": CONFIG_SERVER_API_KEY}
    c = core.CoreAPI(CORE_USER, CORE_PASS, CORE_ENV)
    offset = 250
    loop = 0
    s = requests.Session()
    s.headers.update(headers)
    s.verify = False
    while(True):
        print "Checking Devices from batch: ", (loop + 1)
        devices = c.get_devices_for_account(CORE_ACCOUNTS,
                                            offset=offset * loop)
        for device in devices:
            account_number = device['account']['load_value']

            try:
                (cell, region) = device['name'].split('.')[1:3]
            except AttributeError as e:
                print "WTF MAN THIS THING HAS NO NAME: %s//%s" % (account_number, device['number'])
                continue

            r = s.post(CONFIG_SERVER, data='{ "containers": [ { "name": "%s" } ] }' % (region))
            r = s.post(CONFIG_SERVER + "/%s" %(region),
                       data='{ "containers": [ { "name": "%s" } ] }' %(cell))

            if device['primary_ip'] is None:
                print "WTF MAN THIS THING HAS NO PRIMARY IP: %s/%s/%s/%s" % (account_number, region, cell, device['number'])
                continue

            data = { "keyvals": list() }
            for key in device.keys():
                if key != 'account':
                    data['keyvals'].append({
                                           "key": key,
                                           "value": device[key]
                                           })
                if key == 'account':
                    data['keyvals'].append({
                                           "key": "account",
                                           "value": account_number
                                           })

            device_name = "-".join(device['primary_ip'].split('.')[1:4]) + "-" + str(device['number'])
            
            uri = '/%s/%s/%s' %(region, cell, device_name)
            r = s.post(CONFIG_SERVER + "/%s/%s" % (region, cell),
                       data='{ "containers": [ { "name": "%s" } ] }' % (device_name))
            r = s.post(CONFIG_SERVER + uri, data='{ "containers" : [ { "name": "core", "description": "core attribute data" } ] }')
            r = s.post(CONFIG_SERVER + uri + "/core", data=json.dumps(data))
            if r.status_code != 200:
                print "Error %d processing:" %(r.status_code)
                print data
                print r.text
                continue

        if len(devices) < offset:
            break

        loop += 1

if __name__ == "__main__":
    sys.exit(main())

