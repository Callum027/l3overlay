#
# IPsec overlay network manager (l3overlay)
# l3overlay/overlay/interface/mesh)tunnel.py - mesh tunnel
#
# Copyright (c) 2016 Catalyst.net Ltd
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


from l3overlay import util

from l3overlay.network.interface import bridge
from l3overlay.network.interface import gre
from l3overlay.network.interface import veth

from l3overlay.overlay.interface import Interface


class MeshTunnel(Interface):
    '''
    Used to configure a mesh tunnel interface.
    '''

    def __init__(self, daemon, overlay, name,
            node_local, node_remote,
            physical_local, physical_remote,
            virtual_local, virtual_remote):
        '''
        Parse the mesh tunnel interface configuration and create
        internal fields.
        '''

        super().__init__(daemon, overlay, name)

        self.node_local = node_local
        self.node_remote = node_remote

        self.physical_local = physical_local
        self.physical_remote = physical_remote

        self.virtual_local = virtual_local
        self.virtual_remote = virtual_remote
        self.virtual_netmask = 127 if util.ip_address_is_v6(self.virtual_local) else 31

        self.bridge_name = "%sbr" % self.name
        self.root_veth_name = "%sv0" % self.name
        self.netns_veth_name = "%sv1" % self.name


    def start(self):
        '''
        Start the mesh tunnel.
        '''

        self.logger.info("starting mesh tunnel '%s'" % self.name)

        tunnel_if = gre.create(
            self.logger,
            self.ipdb,
            self.name,
            "gretap",
            self.physical_remote,
            self.physical_key,
            self.daemon.gre_key(physical_local, physical_remote),
        )

        root_veth_if = veth.create(
            self.logger,
            self.root_ipdb,
            self.root_veth_name,
            self.netns_veth_name,
        )

        netns_veth_if = interface.netns_set(
            self.logger,
            self.ipdb,
            self.netns_veth_name,
            self.netns,
        )

        bridge_if = bridge.create(self.logger, self.daemon.root_ipdb, self.bridge_name)
        bridge_if.add_port(tunnel_if)
        bridge_if.add_port(root_veth_if)

        # Add an address to the network namespace veth interface, so it can
        # be addressed from either side of the mesh tunnel.
        netns_veth_if.add_ip(self.virtual_local, self.virtual_netmask)

        tunnel_if.up()
        root_veth_if.up()
        netns_veth_if.up()
        bridge_if.up()

        self.logger.info("finished starting mesh tunnel '%s'" % self.name)

        ## Add the mesh tunnel to the list of routed interfaces.
        #logging.debug("adding BGP route for mesh tunnel %s" % gretap_name)

        #mesh_tunnel = {
        #    'interface': gretap_name,

        #    'local': {
        #        'name': link[0],
        #        'address': netns_veth_address_local,
        #    },

        #    'remote': {
        #        'name': link[1],
        #        'address': netns_veth_address_remote,
        #    },
        #}

        #if Util.ip_network_is_v6(self.linknet_pool):
        #    self.bird6_config_add('mesh_tunnels', [mesh_tunnel])
        #else:
        #    self.bird_config_add('mesh_tunnels', [mesh_tunnel])



    def stop(self):
        '''
        Stop the mesh tunnel.
        '''

        self.logger.info("stopping mesh tunnel '%s'" % self.name)

        bridge.get(self.logger, self.root_ipdb, self.bridge_name).remove()
        veth.get(self.logger, self.root_ipdb, self.outer_name).remove()
        gre.get(self.logger, self.root_ipdb, self.name).remove()

        self.logger.info("finished stopping mesh tunnel '%s'" % self.name)


Interface.register(Tunnel)
