import os
_basedir = os.path.abspath(os.path.dirname(__file__))

"""
General Behavior Settings
"""
# The default tag for configuration items. This will always be made uppercase
DEFAULT_TAG = 'GLOBAL'

"""
Security Settings
"""
# Path to keyczar keys
KEYPATH = '/Users/ephur/Projects/VirtualEnvs/crudconfig2/crud_config/etc/keys'
# Used to keep sessions secure ; unimplemented
SECRET_KEY = 'jgtTMdRkuwmMfwYf9j4hryJVMCnsMCToYvPM3zgKW3vVUnwpe7whHumstNUg'

"""
Database Connection Settings
"""
# Database server host (IP Adress or Hostname)
DATABASE_HOST = "localhost"
# Port to connect to on the DB Server
DATABASE_PORT = 3306
# Username for DB Connections
DATABASE_USER = "cc"
# Password for DB Connections
DATABASE_PASS = "cc_test"
# Database to use
DATABASE_DB = "crud_config"


"""
Cache settings
"""
# Memcache servers, a comma separated list
MEMCACHE_SERVERS = '127.0.0.1:11211'
# How long should other threads wait on a page that is loading details into
# cache (MAX). Setting this value to low will reduce caching efficiency and
# could decrease performance
CACHE_LOCKING_SECONDS = 3
# Default TTL of items in the cache
CACHE_DEFAULT_AGE_SECONDS = 600
# How long to cache auth requests for in seconds
CACHE_AUTH = 60*60*3