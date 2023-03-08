
Not sure exactly how this works, other comment is:

To be run in:

    sudo cumin 'P{P:netbox::host%location ~ "A.*codfw"}' 'grep "^- " /etc/wikimedia/contacts.yaml' -i


