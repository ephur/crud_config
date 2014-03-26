BETA: Some things don't work!
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
* post /  (Create new containers / keyvalues in the global area)

```json
{
    "containers": [{
        "name": "c0099",
        "description": "Cell 0099 in DFW"
    }, {
        "name": "c0100",
        "description": "Cell c0100 in DFW"
    }],
    "keyvals": [{
        "key": "a_key",
        "tag": "v499",
        "value": "a_value"
    }, {
        "key": "b_key",
        "value": "b_value"
    }]
}
```

* post / (Create keyvalues in the global area)

```json
{
    "keyvals": [{
        "key": "a_key",
        "tag": "v499",
        "value": "a_value"
    }, {
        "key": "b_key",
        "value": "b_value"
    }]
}
```

* post /path/to/a/container  (Create new containers/keyvalues in the container at this path)

```json
{
    "containers": [{
        "name": "c0099",
        "description": "Cell 0099 in DFW"
    }, {
        "name": "c0100",
        "description": "Cell c0100 in DFW"
    }],
    "keyvals": [{
        "key": "a_key",
        "tag": "v499",
        "value": "a_value"
    }, {
        "key": "b_key",
        "value": "b_value"
    }]
}
```

* post /path/to/a/container (Create keyvalues in the container at this path)

```json
{
    "keyvals": [{
        "key": "a_key",
        "tag": "v499",
        "value": "a_value"
    }, {
        "key": "b_key",
        "value": "b_value"
    }]
}
```


## RETRIEVE: retrieve configuration information
A key is optional in get operations, but does change the behavior of the return. If no key is provided, then ALL keys defined at the level requested are returned, optionally keys matching the tagare returned. If a particular key is requested.

*NOTE:* This structure is dynamic, and can look however the 'containers' are organized into a tree. The tree below merely reflects our organization. The organization can be changed. Each item (region, cell, machine) is merely a container, and the get request path reflects the organization of the tree. 

### get requests
* get /[?key=y&tag=x] (get [a] config value[s] from the global area )
* get /region[?key=y&tag=x] (get [a] config value[s] from a region)
* get /region/cell[?key=y&tag=x] (get [a] config value[s] from a cell)
* get /region/cell/machine[?key=y&tag=x] (get [a] config value[s] from a machine)

Parameters:
return (get /container?return=ALL)
* VALUES - Return  a dictionary of keys and values (DEFAULT)
* ALL - Return a dictionary of both keyvalues and containers
* CONTAINERS - Return a dictionary of containers & info about containers


### Retrieve Containers

### get requests
Get the list of containers at the root
```
get /[container]?return=[all,containers]
get /operations/container/list/[container]
```

Get list of containers in a container
```
get /operations/container/list/path/to[container]
```

Get containers recursively
```
get /operations/container/list/[container]\?recursive\=true
```

### Search & Retrieve Container Contents

### get requests
Return a dictionary of all nested containers and their content, holding a specified key.
```
get /operations/container/content/[container to search]?key=X
```

Return a dictionary of all nested containers and their content, holding a specified key value pair.
```
get /operations/container/content/[container to search]?key=X&value=Y
```

## UPDATE: update existing configuration values
Update configuration values. You can not update a value that does not exist. A 404 will be returned if updating a value that does not exist. It is optional to provide a tag, if a tag is not provided it will be assumed to be a global value. If a tag is provided, that tag must exist to update.

##### put requests
* put /key?value=x[&tag=y]  (update a key)
* put /region/key?value=x[&tag=y] (update a key)
* put /region/cell/key?value=x[&tag=y] (update a key)
* put /region/cell/machine/key?value=x&[tag=y] (update a key)

* put / (update one more more keys at the global level)

``
{"keyvals": [{ "key":"key_name", "value":"value", "tag":"value2"}, { "key":"key2_name", "value":"value2", "tag":"value2"} ]}
``

* put /region (update one more more keys, at this level of the hierarchy)

``
{"keyvals": [{ "key":"key_name", "value":"value", "tag":"value2"}, { "key":"key2_name", "value":"value2", "tag":"value2"} ]}
``

* put /region/cell (update one more more keys, at this level of the hierarchy)

``
{"keyvals": [{ "key":"key_name", "value":"value", "tag":"value2"}, { "key":"key2_name", "value":"value2", "tag":"value2"} ]}
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
