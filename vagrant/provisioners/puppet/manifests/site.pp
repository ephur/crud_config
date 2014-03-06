package { 'python-pip': ensure => present }
package { 'python-dev': ensure => present }
package { 'libmemcached-dev': ensure => present }
package { 'libssl-dev': ensure => present }
package { 'build-essential': ensure => present }

# Setup all of the mysql stuff
# This creates a database named crud_config, with user cc and password cc_test

class { '::mysql::server': root_password => 'qwerty' }
class { '::mysql::client': }
package { 'libmysqlclient-dev': ensure => present }


mysql_database { 'crud_config':
  ensure  => 'present',
}

# The actual password is cc_test but mysql excepts the crazy hash
mysql_user { 'cc@localhost':
  ensure => 'present',
  password_hash => '*A6603D12CF0DF7C69F3AD9C2F164460FBC31A75E',
}

mysql_grant { 'cc@localhost/crud_config.*':
  ensure     => 'present',
  options    => ['GRANT'],
  privileges => ['ALL'],
  table      => 'crud_config.*',
  user       => 'cc@localhost',
}

# Always nice to have ipython around
package { 'ipython': ensure	=> present }

package { 'python-mysqldb':
  ensure => installed,
}

package { 'Flask':
  ensure   => present,
  provider => pip,
  require  => Package['python-pip']
}

package { 'Flask-SQLAlchemy':
  ensure   => present,
  provider => pip,
  require  => [ Package['python-pip'], Package['Flask'] ]
}

package { 'simplejson':
  ensure      => present,
  provider    => pip,
  require     => Package['python-pip']
}

package { 'pylibmc':
  ensure      => present,
  provider    => pip,
}

package { 'requests':
  ensure      => installed,
  provider    => pip,
}

package {'alembic':
	ensure		=> installed,
	provider	=> pip,
}	

package { 'memcached': ensure => present }
