#!/usr/bin/env python
import sys
import requests
import simplejson as json
import time
from config import *


def main():
    query = {'sql': 'select * from compute_nodes'}
    headers = { "X-API-Auth": CONFIG_SERVER_API_KEY}
    #r = requests.post(auth=(SSO_USER, SSO_PASSWORD))
    for region in ENVIRONMENT.keys():
        s=requests.Session()
        s.headers.update(headers)
        s.verify = False
        # Create the region at the top level
        r = s.post(CONFIG_SERVER, data=json.dumps({"containers": [ { "name": region } ] }))
        for cell in ENVIRONMENT[region]:
            post_times = []
            get_times = []
            put_times = []
            # Create a cell inside the region
            start_time = time.time()
            r = s.post(CONFIG_SERVER + "/" + region, data=json.dumps({"containers": [ { "name": cell } ] }))
            post_times.append(time.time() - start_time)
            print "Processing %s/%s" %(region, cell)
            # Build the URI and make request to JSON Bridge
            uri = "%s/query/prod.%s.%s.nova" % (JSON_BRIDGE, region, cell)
            r = s.post(uri, data=query, auth=(SSO_USER, SSO_PASS),
                              verify=False)

            # The return should be a list of hypervisors
            try:
                hypervisors = r.json()['result']
            except Exception as e:
                print e.message
                print r.text
                print r.json()
                raise

            loop=1
            for hypervisor in hypervisors:
                # Create the objects for the config item post request
                put_data = list()
                post_data = list()
                # The name is the item created
                try:
                    name = hypervisor.pop("hypervisor_hostname")
                except KeyError as e:
                    print("Hypervisor Hostname missing!")
                # The URI is the config server/region/cell
                uri = "%s/%s/%s" % (CONFIG_SERVER, region, cell)
                start_time = time.time()
                r = s.post(uri, data=json.dumps({ "containers": [ { "name": name } ] }))
                post_times.append(time.time() - start_time)
                uri = "%s/%s/%s/%s" % (CONFIG_SERVER, region, cell, name)
                r = s.post(uri,
                           data=json.dumps({"containers": [ { "name": "nova", "description": "nova DB config objects"} ] }))
                uri = "%s/%s/%s/%s/nova" % (CONFIG_SERVER, region, cell, name)
                start_time = time.time()
                r = s.get(uri)
                if r.status_code == 404:
                    existing_keys = dict()
                else:
                    existing_keys = r.json()
                get_times.append(time.time() - start_time)
                for key in hypervisor.keys():
                    if key in existing_keys.keys():
                        put_data.append( { "key": key, "value": str(hypervisor[key]) } )
                    else:
                        post_data.append( { "key": key, "value": str(hypervisor[key]) } )
                if len(put_data) > 0:
                    start_time = time.time()
                    r = s.put(uri,data=json.dumps({"keyvals": put_data }))
                    put_times.append(time.time() - start_time)
                if len(post_data) > 0:
                    start_time = time.time()
                    r = s.post(uri,data=json.dumps({"keyvals": post_data }))
                    put_times.append(time.time() - start_time)
                if loop == 25:
                    loop = 1
                    sys.stdout.write(".")
                else:
                    loop += 1
            print "oOo.... DONE! (average get/put/post/ times: %f/%f/%f seconds)" % (
                     sum(get_times) / float(len(get_times)),
                     sum(put_times) / float(len(put_times)),
                     sum(post_times) / float(len(post_times)),
                     )


if __name__ == "__main__":
    sys.exit(main())

