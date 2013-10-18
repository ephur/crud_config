ALPHA: The things don't work! 
====

# Crud Config
A simple service that supports the following operations to store/read configuration data. The data is backed by a mySQL database (currently, probably easy to change if you want a flavor of the month).


*Tags*: All data values are stored tagged, so you can match them up to a particular release, except for one special tag named GLOBAL. If no other tag is specified, GLOBAL is the default tag assumed. This tag name can be changed via the configuration. 

*Data Security*: KeyCzar is used to store ALL configuration values encrypted in the database, this is done in order to ensure

*Inheritance*: Configuration values inherit Global/Regional/Cell level settings. For example, a request for the "name" value on a cell will first check the cell, and if not defined there, it will check the region, and if not defined there it will check the top level configurations. The first matching one is returned, this allows overrides for particular items to be set while allowing defaults to be set for larger collecitons. 


## CREATE: create config values
Create new values in the configuration store. If a value already exists a 422 will be returned. You need to do a PUT instead against this. The key and tag together must be unique. If a tag is not defined it is assumed to be global for the level of configuration. 

In post requests, you can include copyfrom in the JSON dictionary, and all keys/values/tags will be copied from an existing region/cell/machine (it must exist in the same container)

### post requests 
* post /config/   (create a new config value in the global area)

``
{[{"key": "value", "tag": "value"}, {"key2": "value2", "tag": "value2" }, [..]}
``

* post /config (create a region in the global area)

``
{region: [name, name2, name3], copyfrom: cell }
``

* post /config/region (create a new config value in a region)

``
{[{"key": "value", "tag": "value"}, {"key2": "value2", "tag": "value2" }, [..]}
``

* post /config/region (create a new cell in a region)

``
{cell: [name, name2, name3], copyfrom: cell }
``

* post /config/region/cell (create a new config value in a cell)

``
{[{"key": "value", "tag": "value"}, {"key2": "value2", "tag": "value2" }, [..]}
``

* post /config/region/cell (create a new machine in a cell)

``
{machine: [name, name2, name3] copyfrom: machine  }
``

* post /config/region/cell/machine

``
{[{"key": "value", "tag": "value"}, {"key2": "value2", "tag": "value2" }, [..]}
``


## RETRIEVE: retrieve configuration information
A key is optional in get operations, but does change the behavior of the return. If no key is provided, then ALL keys defined at the level requested are returned, optionally keys matching the tag
are returned. If a particular key is requested 

### get requests
* get /config/[key?tag=x] (get [a] config value[s] from the global area )
* get /config/?regions (get all the regions in the global area)
* get /config/region[key?tag=x] (get [a] config value[s] from a region)
* get /config/regions/?cells (get all the cells in a region)
* get /config/region/cell/[key?tag=x] (get [a] config value[s] from a cell)
* get /config/region/cell/?machines (get all the machines in a region)  
* get /config/region/cell/machine[key?tag=x] (get [a] config value[s] from a machine)


## UPDATE: update existing configuration values
Update configuration values. You can not update a value that does not exist. A 404 will be returned if updating a value that does not exist. It is optional to provide a tag, if a tag is not provided it will be assumed to be a global value. If a tag is provided, that tag must exist to update.

##### put requests
* put /config/key?value=x[&tag=y]  (update a key)
* put /config/region/key?value=x[&tag=y] (update a key)
* put /config/region/cell/key?value=x[&tag=y] (update a key)
* put /config/region/cell/machine/key?value=x&[tag=y] (update a key)

* put /config/key (update one more more keys)

``
{[{"key": "value", "tag": "value"}, {"key2": "value2", "tag": "value2" }, [..]}
``

* put /config/region (update one more more keys)

``
{[{"key": "value", "tag": "value"}, {"key2": "value2", "tag": "value2" }, [..]}
``

* put /config/region/cell (update one more more keys)

``
{[{"key": "value", "tag": "value"}, {"key2": "value2", "tag": "value2" }, [..]}
``

* put /config/region/cell/machine (update one more more keys)

``
{[{"key": "value", "tag": "value"}, {"key2": "value2", "tag": "value2" }, [..]}
``

## DELETE OPERATIONS

### delete requests 
* delete /config/key?tag=y (delete a key with matching tag from the global area)
* delete /config/region?yes_im_sure=true (delete a region and matching keys)
* delete /config/region/key?tag=y (delete a key with matching tag from a region)
* delete /config/region/cell?yes_im_sure=true (delete a cell and matching keys)
* delete /config/region/cell/key?tag=y (delete a key with matching tag from from a cell)
* delete /config/region/cell/machine/key&tag=y (delete a key with matching tag from a machine)
* delete /config/region/cell/machine?yes_im_sure=true (delete a machine and matching keys)

## AUTH MECHANISM: 
### LDAP/SSO:
Provide headers:
{ X-SSO-Auth: username:password }

### INTERNAL API KEY:
{ X-API-Auth: APIKEY }

## DATA FORMAT MECHANISMS:
To change the returned data format, provide the proper header type 
* JSON: { Accept: application/json }  (default)
* YAML: { Accept: text/yaml }
* TEXT: { Accept: }

##SERVICE CONFIGURATION OPTIONS: 
*keypath*: The path where keyczar keys are located for handling encrypted data
*global_tag*: The tag to apply to 'global' configuration values
*ldap_server*: LDAP server to use for LDAP based authentication 
