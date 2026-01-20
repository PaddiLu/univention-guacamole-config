#!/usr/bin/python3
# -*- coding: utf-8 -*-

# SPDX-FileCopyrightText: 2026 Patrick Lübcke
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Module for Univention Directory Manager (UDM) to provide
connection settings for Apache Guacamole servers
"""

# NOTE: This module only works with non-standard LDAP ObjectClass guacConfigGroup
# with OID 2.25.168357219212813334508930408357184981976


import univention.admin.handlers
import univention.admin.localization
import univention.admin.syntax
from univention.admin.layout import Group, Tab
from univention.admin.uldap import DN


# Localization
translation = univention.admin.localization.translation('univention.admin.handlers.guacamole-config')
_ = translation.translate


# Syntax definitions
class GuacamoleProtocols(univention.admin.syntax.select):
    """Syntax for a selection list of Guacamole-compatible protocols"""
    name = _("Connection Protocol")
    choices = [('kubernetes',_('Kubernetes')),('rdp',_('RDP')),('ssh',_('SSH')),('telnet',_('Telnet')),('vnc',_('VNC'))]
    size = 'Half'

class GuacdEncryptions(univention.admin.syntax.select):
    """Syntax for a selection list of encryption methods used by guacd"""
    name = _("Encryption")
    empty_value = True
    choices = [('NONE',_("None")),('SSL',_('SSL'))]
    default = ''
    size = 'OneThird'


# Metadata
module = 'guacamole-config/connection'
childs = False
short_description = _('Guacamole Connection')
long_description = _('Configuration for an Apache Guacamole connection')
operations = ['add', 'edit', 'remove', 'search', 'move']

options = {
    'default': univention.admin.option(
        short_description = short_description,
        default = True,
        objectClasses = ['top','guacConfigGroup'],
    ),
}

property_descriptions = {
    'name': univention.admin.property(
        short_description = _("Name"),
        syntax = univention.admin.syntax.string,
        include_in_default_search = True,
        required = True,
        identifies = True,
    ),
    'description': univention.admin.property(
        short_description = _("Description"),
        syntax = univention.admin.syntax.string,
        include_in_default_search = True,
    ),
    'protocol': univention.admin.property(
        short_description = _("Protocol"),
        long_description = _("The protocol used to connect to the host"),
        syntax = GuacamoleProtocols,
        required = True,
        include_in_default_search = True,
    ),
    'parameter': univention.admin.property(
        short_description = _("Parameter"),
        long_description = _("Connection parameters, given as name=value"),
        syntax = univention.admin.syntax.string,
        multivalue = True,
        include_in_default_search = True,
    ),
    'user': univention.admin.property(
        short_description = _("Users"),
        long_description = _("Users that may access this configuration"),
        syntax = univention.admin.syntax.UserDN,
        multivalue = True,
        dontsearch = True,
  		readonly_when_synced = True,
		copyable = True,
    ),
    'group': univention.admin.property(
        short_description = _("Groups"),
        long_description = _("Groups whose members may access this configuration"),
        syntax = univention.admin.syntax.GroupDN,
        multivalue = True,
        dontsearch = True,
  		readonly_when_synced = True,
		copyable = True,
    ),
    'proxyname': univention.admin.property(
        short_description = _("Hostname"),
        long_description = _("The host name or IP address to use to connect to guacd (default if empty)"),
        syntax = univention.admin.syntax.hostOrIP,
        include_in_default_search = True,
    ),
    'proxyport': univention.admin.property(
        short_description = _("Port"),
        long_description = _("The TCP port to use to connect to guacd (default if empty)"),
        syntax = univention.admin.syntax.integer,
        dontsearch = True,
        size = 'OneThird',
    ),
    'proxyencryption': univention.admin.property(
        short_description = _("Encryption"),
        long_description = _("The encryption method to use to connect to guacd (default if empty)"),
        syntax = GuacdEncryptions,
        dontsearch = True,
    ),
}

layout = [
    Tab(_("General"), _("Basic Settings"), layout=[
        ["name","description"],
        Group(_("Connection Settings"), layout=[
            "protocol",
            "parameter",
        ]),
    ]),
    Tab(_("Users"), _("Access Control"), layout=[
        ["user","group"],
    ]),
    Tab(_("Proxy"), _("guacd Proxy Settings"), layout=[
        ["proxyname","proxyport"],
        "proxyencryption",
    ]),
]


# Mapping of UDM properties to LDAP attributes
mapping = univention.admin.mapping.mapping()

mapping.register('name', 'cn', None, univention.admin.mapping.ListToString)
mapping.register('description', 'description', None, univention.admin.mapping.ListToString)

mapping.register('protocol','guacConfigProtocol', None, univention.admin.mapping.ListToString)
mapping.register('parameter','guacConfigParameter')

mapping.register('proxyname','guacConfigProxyHostname', None, univention.admin.mapping.ListToString)
mapping.register('proxyport','guacConfigProxyPort', None, univention.admin.mapping.ListToString)
mapping.register('proxyencryption','guacConfigProxyEncryption', None, univention.admin.mapping.ListToString)

# Properties 'user' and 'group' are handled manually in class object


class object(univention.admin.handlers.simpleLdap):
    module = module

    def open(self) -> None:
        """Open the LDAP object"""

        def _readout_attributes(fieldname: str) -> list:
            output = []
            for attribute in self.oldattr.get(fieldname, []):
                output.append(attribute.decode("UTF-8"))
            return output

        super(object, self).open()

        if not self.exists():
            return

        self['user'] = _readout_attributes('uniqueMember')
        self['group'] = _readout_attributes('seeAlso')
        self.save()

    def _ldap_modlist(self):
        """Create a LDAP modlist"""

        def _list_changes(fieldname: str, attrname: str) -> list:
            output = list()
            oldset = DN.set(self.oldinfo.get(fieldname, []))
            newset = DN.set(self.info.get(fieldname, []))
            if oldset == newset:
                return output
            additions = [x.encode("utf-8") for x in DN.values(newset - oldset)]
            removals = [x.encode("utf-8") for x in DN.values(oldset - newset)]
            if additions:
                output.append((attrname, b"", additions))
            if removals:
                output.append((attrname, removals, b""))
            return output

        ml = super(object, self)._ldap_modlist()

        ml.extend(_list_changes("user", "uniqueMember"))
        ml.extend(_list_changes("group", "seeAlso"))
        return ml


lookup = object.lookup
lookup_filter = object.lookup_filter
identify = object.identify
