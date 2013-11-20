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
    parser_list.add_argument('-d','--depth', help='How deep to recurse (default: 10)', type=int, default=10)
    # The 'get' command -- get values in a container
    parser_get = subparsers.add_parser('get', help='Get Values from Container')
    parser_get.add_argument('path', help='container to get values from')
    parser_get.add_argument('-k','--key', help='get value for a particular key')
    parser_get.add_argument('-t','--tag', help='match values for specific tag')

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

    def list(self):
        queryparams=dict()
        if self._args.recursive is True:
            queryparams['recursive'] = 'true'
            queryparams['depth'] = self._args.depth
        path = "/operations/container/list/" + self._args.path.lstrip('/')
        print self.yaml(self._get(path, params=queryparams))
        return 0

    def get(self):
        queryparams=dict()
        if self._args.key is not None:
            queryparams['key'] = self._args.key
        if self._args.tag is not None:
            queryparams['tag'] = self._args.tag

        path = self._args.path.lstrip('/')
        print self.yaml(self._get(path, params=queryparams))
        return 0


    def _get(self, path, params=dict()):
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
        return r.text

    def yaml(self, data):
        return yaml.dump(yaml.load(data),
                         default_flow_style=False)

if __name__ == "__main__":
    sys.exit(main())