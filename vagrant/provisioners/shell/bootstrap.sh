#!/usr/bin/env bash

# Make sure that git and librarian-puppet is installed

if ! which git ; then
    apt-get update
    apt-get install -y git
fi

if ! which librarian-puppet ; then
    gem install --no-ri --no-rdoc librarian-puppet
    # Silly hack to handle using the o3squeeze base box
    if ! which librarian-puppet ; then
        ln -s /var/lib/gems/1.8/bin/librarian-puppet /usr/local/bin/.
        apt-get install curl
    fi
fi
