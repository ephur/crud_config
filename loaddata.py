#!/usr/bin/env python 

import crudconfig

cconfig = crudconfig.CrudConfig(keypath="/Users/ephur/Projects/VirtualEnvs/crudconfig2/crud_config/etc/keys", 
	                       db_name='crud_config',
	                       db_username='cc',
	                       db_password='cc_test',
	                       db_host='localhost')

regions = ['dfw', 'ord', 'lon', 'hkg', 'syd']
cells = ['c0001', 'c0002', 'c0003', 'c0004', 'c0005', 'c0006', 'a0001', 'b0001', 'a.b-0001']
keys = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 
        'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 
        's', 't', 'u', 'v', 'w', 'x', 'y', 'z' ]

node_count = 600

root = cconfig.get_container("/")
for region in regions: 
	# rc is the region container
	# cconfig.new_session()
	rc = cconfig.add_container(root.id, region)
	for cell in cells:
		print "Working %s/%s" % (region, cell)
		# cconfig.new_session()
		cc = cconfig.add_container(rc.id, cell)
		for machine in range(node_count):
			# cconfig.new_session()
			node = "compute-node-" + str(machine)
			path = "%s/%s/%s" % (region, cell, node)
			mc = cconfig.add_container(cc.id, node)
			(k, v) = cconfig.add_keyval(path, "region", region)
			(k, v) = cconfig.add_keyval(path, "cell", cell)
			(k, v) = cconfig.add_keyval(path, "name", machine)
			(k, v) = cconfig.add_keyval(path, "region", region)
			(k, v) = cconfig.add_keyval(path, "list", "item1")
			(k, v) = cconfig.add_keyval(path, "list", "item2")
			(k, v) = cconfig.add_keyval(path, "list", "item3")
			for key in keys:
				(k, v) = cconfig.add_keyval(path, key, key + "-" + str(machine) )