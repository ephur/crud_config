import sys
import os
import ConfigParser
import argparse
import requests
import yaml

try:
    import simplejson as json
except ImportError:
    import json as json

try:
    import keyring
    import getpass
    import re
    KEYRING = True
except ImportError:
    KEYRING = False

# Default configuration file
CONFIG_FILE=os.getenv("HOME") + "/.crud_config.ini"

# Descritpion of program
PROG_DESCRIPTION="""The Crud Config CLI is a tool meant to make getting and setting values in crud config reallllly easy!"""

# Any warning text to be displayed after usage
PROG_WARNING=''
VERSION='0.1'
SSL_VERIFY=False

def main():
    args = load_args()
    config = load_config(args.config_file)

    if config.get("crud","auth_type") == "API_KEY":
        cc = crud(apikey=config.get("crud","api_key"), args=args, config=config)
    elif config.get("crud","auth_type") == "SSO":
        pass
    else:
        print "Invalid auth type in config (must be API_KEY or SSO)"
        return 1
    return(getattr(cc, args.action)())

def load_config(config_file):
    # Read the config file
    try:
        config = ConfigParser.ConfigParser()
        config.readfp(open(config_file))
    except IOError as e:
        print "Unable to read configuration file %s" % (config_file)
        sys.exit(1)
    return config

def load_args():
    parser = argparse.ArgumentParser(description=PROG_DESCRIPTION,
                                     epilog=PROG_WARNING,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-c","--config-file", help="configuration file for dns script (default:%s)" % (CONFIG_FILE), default=CONFIG_FILE, type=str)
    parser.add_argument("-v","--verbose", help="more verbose output in random places!", action="store_true")
    parser.add_argument("--update-keychain", help="prompt to update keychain entries (if you're using them!)", action="store_true")
    parser.add_argument("-V","--version", action="version", version='%(prog)s ' + str(VERSION))

    subparsers = parser.add_subparsers(dest="action")
    # The 'list' command -- list containers inside another container
    parser_list = subparsers.add_parser('list', help="List Containers")
    parser_list.add_argument('path', help='container path to list from')
    parser_list.add_argument('-r','--recursive', help='Recursively list items', action="store_true")
    parser_list.add_argument('-d','--depth', help='How deep to recurse (default: 2)', type=int, default=2)
    # The 'get' command -- get values in a container
    parser_get = subparsers.add_parser('get', help='Get Values from Container')
    parser_get.add_argument('path', help='container to get values from')
    parser_get.add_argument('-k','--key', help='get value for a particular key')
    parser_get.add_argument('-t','--tag', help='match values for specific tag')
    # The 'load' command, create keyvals from a YAML file.
    parser_load = subparsers.add_parser('load', help='Load values into a container from a YAML file')
    parser_load.add_argument('path', help='container to load values into')
    parser_load.add_argument('file', help='yaml file to load values from')
    parser_load.add_argument('-t','--tag', help='tag to apply to values loaded from YAML')
    parser_load.add_argument('-c','--create', help='create container if it doesn\'t already exist')
    # Delete a container
    parser_delete_container = subparsers.add_parser('delete_container', help='Delete a container (THIS IS RECURSIVE, CAREFUL!')
    parser_delete_container.add_argument('path', help='path containing container(s) to delete')
    parser_delete_container.add_argument('containers', help='container to delete', nargs='+')

    args = parser.parse_args()
    return args

class crud(object):

    def __init__(self, *args, **kwargs):
        self._session = requests.Session()
        self._config = kwargs['config']
        self._args = kwargs['args']

        try:
            self._session.headers.update({"X-API-Auth": kwargs['apikey']})
        except KeyError as e:
            raise "unable to set authentication information for crud config calls"

        try:
            self._session.verify = self._config.get("crud", "ssl_verify")
        except ConfigParser.NoOptionError as e:
            self._session.verify = SSL_VERIFY

    def load(self):
        path = self._args.path.lstrip('/')
        data = { "keyvals": list() }
        deldata = { "keyvals": list() }
        with open(self._args.file) as f:
            yamldata = yaml.load(f)

        for (k, v) in yamldata.iteritems():
            delval = { "key": k}
            keyval = {
                "key": k,
                "value": v
            }
            if self._args.tag is not None:
                delval['tag'] = self._args.tag
                keyval['tag'] = self._args.tag

            data['keyvals'].append(keyval)
            deldata['keyvals'].append(delval)

        self.__post(path, data=deldata,method='delete')
        print "removed old values"
        self.__post(path, data=data)
        print "added new values"

    def delete_container(self):
        path = self._args.path.lstrip('/')
        data = { "containers": [ x for x in self._args.containers ] }
        self.__post(path, data=data, method='delete')
        print "deleted container"

    def list(self):
        queryparams=dict()
        if self._args.recursive is True:
            queryparams['recursive'] = 'true'
            queryparams['depth'] = self._args.depth
        path = "/operations/container/list/" + self._args.path.lstrip('/')
        print self.yaml(json.dumps(self.__get(path, params=queryparams)))
        return 0

    def get(self):
        queryparams=dict()
        if self._args.key is not None:
            queryparams['key'] = self._args.key
        if self._args.tag is not None:
            queryparams['tag'] = self._args.tag

        path = self._args.path.lstrip('/')
        # print self.yaml(self.__get(path, params=queryparams))
        data = self.__get(path, params=queryparams)
        for k, v in data.iteritems():
            if len(v['values']) == 1:
                print "%s: %s" % (k, v['values'][0]['value'])
            elif len(v['values']) == 0:
                print "%s:" % (k)
            else:
                for val in v.values:
                    print "    - %s" (val.value)

        return 0

    def __post(self, path, data=None, params=dict(), method='post'):
        try:
            uri = "%s/%s" % (
                  self._config.get("crud","config_server").strip('/'),
                  path.lstrip('/'))

        except ConfigParser.NoOptionError as e:
            print "unable to get config_server from %s" % (self._args.config_file)
            return 1

        m = getattr(self._session, method.lower())
        r = m(uri, data=json.dumps(data), verify=False)
        return r.json()

    def __get(self, path, params=dict()):
        paramstr = '&'.join(['%s=%s' % ( k, v ) for k, v in sorted(params.iteritems())])
        try:
            uri = "%s/%s?%s" % (
                  self._config.get("crud","config_server").strip('/'),
                  path.lstrip('/'),
                  paramstr)

        except ConfigParser.NoOptionError as e:
            print "unable to get config_server from %s" % (self._args.config_file)
            return 1

        r = self._session.get(uri, verify=False)
        return r.json()

    def yaml(self, data):
        return yaml.dump(yaml.load(data),
                         default_flow_style=False)

if __name__ == "__main__":
    sys.exit(main())