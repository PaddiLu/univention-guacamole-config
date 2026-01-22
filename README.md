# univention-guacamole-config

This is an extension for _Univention Corporate Server_. It lets you create and manage _Apache Guacamole_ connection settings as LDAP objects. These connections can be accessed by Guacamole clients which use UCS for user authentification.

## Setting up on UCS

> [!WARNING]
> This package will conflict with the Guacamole app for UCS 5.0 from the Univention App Center.\
> They should not be installed alongside each other.

Download the .deb package onto UCS and install with `dpkg -i`.

### Adding connections via Univention Managent Console

Log into Univention Management Console, access __Domain/LDAP Directory__ and add an object of type __Guacamole Connection__.

### Adding connections via command line interface

To create connection settings via the command line, use the following template:
```
univention-directory-manager guacamole-config/connection create \
--position cn=directory,dc=example,dc=net \
--set name=localhost \
--set description="Connect to localhost" \
--set protocol=ssh \
--append parameter=hostname=localhost \
--append parameter=username='${GUAC_USERNAME}' \
--append parameter=password='${GUAC_PASSWORD}' \
--append user=uid=Administrator,cn=users,dc=example,dc=net \
--append group=cn="Domain Users",cn=groups,dc=example,dc=net
```

## Setting up on Guacamole

Instructions on how to connect a Guacamole client to an LDAP server [can be found here](https://guacamole.apache.org/doc/gug/ldap-auth.html#associating-ldap-with-a-database-recommended).

For the Guacamole client to access connections created with this extension, the settings file `guacamole.properties` must include the following line: 
```
ldap-member-attribute: 'uniqueMember'
```
If deploying Guacamole via Docker Compose, instead set the following environment variable: 
```
LDAP_MEMBER_ATTRIBUTE: 'uniqueMember'
```

## Compatibility

This package was only tested with Univention Corporate Server 5.2 and Guacamole 1.6.0
