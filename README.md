l3overlay
=========

l3overlay is a tool used to build a MPLS-like VRF network between nodes/firewalls across the Internet. It uses a combination of network namespaces and gretap tunnels (with optional IPsec encapsulation for security) to create an "overlay" over the participating nodes' Internet connections.

Prerequisites
-------------

The following software packages are required to run l3overlay:

* **Python**, version **3.4** or later
* **iproute2**
* **BIRD** routing daemon, version **1.4.0** or later
* **strongSwan** IPsec

The following Python modules must also be installed:

* **pyroute2**, version **0.4.6** or later
* **jinja2**

The following configuration settings should be set in `/etc/sysctl.conf`, to enable IPv4 (and IPv6 if desired) packet forwarding:

    net.ipv4.ip_forward=1
    net.ipv6.conf.all.forwarding=1

If you intend to use the static VLAN functionality in the overlay, the following Linux kernel module should be enabled by inserting this line into `/etc/modprobe.conf`, if it is not enabled by default:

    8021q

Installation
------------

l3overlay can be installed to the default location by simply using:

    sudo make install

By default, this will install the `l3overlayd` executable into `/usr/local/sbin`, and it will make a configuration hierarchy in `/usr/local/etc/l3overlay`.

See the `Makefile` for more details on how to change the installation locations.

`l3overlayd` looks for files in the following directories, in the order shown:

1. `(current working directory)`
2. `(current working directory)/etc/l3overlay`
3. `(current working directory)/../etc/l3overlay`
4. `(executable directory)`
5. `(executable directory)/etc/l3overlay`
6. `(executable directory)/../etc/l3overlay`
7. `/etc/l3overlay`

Any configuration files or directories mentioned in this document should be placed in any of the directories mentioned above. For instance, assuming `/etc/l3overlay` is the chosen directory, the global configuration and a test overlay configuration would be placed in the following filepaths:

* `/etc/l3overlay/global.conf`
* `/etc/l3overlay/overlays/example.conf`

Running
-------

Once l3overlay is installed and configured, it can be executed by simply running the `l3overlayd` command if it is located in the `PATH` environment variable, or by running the executable directly if it is not.

If the `WITH_UPSTART` or `WITH_INIT_D` configuration options were specified when installing l3overlay, an Upstart configuration or `/etc/init.d` script would have been installed with l3overlay.

To start l3overlay as a service, simply run:

    sudo service l3overlay start

To ensure that l3overlay starts with the system using the `/etc/init.d` script, this command should also be run:

    sudo update-rc.d l3overlay defaults

All of the directories and files that `l3overlayd` uses can be specified on the command line. The command `l3overlayd --help` documents the command line switches which can be used:

    usage: l3overlayd [-h] [-gc FILE] [-ocd DIR] [-oc FILE [FILE ...]] [-td DIR]
                      [-fsd DIR] [-Ld DIR] [-lf FILE] [-pf FILE]

    Construct one or more MPLS-like VRF networks using IPsec tunnels and network
    namespaces.

    optional arguments:
      -h, --help            show this help message and exit
      -gc FILE, --global-conf FILE
                            use FILE as the global configuration file
      -ocd DIR, --overlay-conf-dir DIR
                            use DIR as the overlay conf search directory
      -oc FILE [FILE ...], --overlay-conf FILE [FILE ...]
                            configure the overlay defined in FILE, disables
                            overlay config directory searching
      -td DIR, --template-dir DIR
                            use DIR as the configuration template search directory
      -fsd DIR, --fwbuilder-script-dir DIR
                            use DIR as the fwbuilder script search directory
      -Ld DIR, --lib-dir DIR
                            use DIR as the runtime data directory
      -lf FILE, --log-file FILE
                            log output to FILE
      -pf FILE, --pid-file FILE
                            use FILE as the PID lock file

Example configuration
----------------------

An example configuration needed to get a working overlay set up may look something like this. More settings are available for the overlays to set up connections to be exposed to the overlay from the nodes, available in the *Global configuration* and *Overlay configuration* sections below.

### global.conf

```ini
[global]
logging-level=INFO
use-ipsec=true
ipsec-psk={psk}
```

### overlays/example.conf (on node example-1)

```ini
[overlay]
name=example
asn=64666
linknet-pool=198.51.100.0/24
this-node=example-1
node-0=example-1 192.0.2.1
node-1=example-2 192.0.2.2
node-2=example-3 192.0.2.3
node-3=example-4 192.0.2.4
```

Global configuration
--------------------

Global configuration values for l3overlay are to be defined in `global.conf`.

This file is optional, since all of the configuration options defined here are not strictly required.

If an IPsec PSK is stored in the global configuration, the permissions should be set such that the user running `l3overlayd` is the only user with read permission to the global configuration.

### [global]

All `global.conf` configuration values come under the `[global]` section.

#### log-level
* Type: **enum**
* Required: no
* Values: `NOTSET`, `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

Specifies the logging output level that l3overlay should use. The default value is `INFO`.

#### use-ipsec
* Type: **boolean**
* Required: no

Specifies whether or not IPsec should be used to encrypt the overlay mesh tunnels. The default value is `false`.

#### ipsec-psk
* Type: **hex**, 6-64 digits
* Required: **yes**, **IF** `use-ipsec` is `true`

The hex string used as the pre-shared key (PSK) for authentication of the IPsec tunnels encapsulating the overlay. The PSK must be at least 6 digits long, and has a maximum length of 64 digits.

#### ipsec-manage
* Type: **boolean**
* Required: no

The default value is `true`. Read the description for this configuration option carefully, as it completely changes the way l3overlay handles IPsec.

If `true`, l3overlay will assume that it is to manage the IPsec daemon. When it does this, it will install the IPsec configuration to `/etc/ipsec.conf`, and it will also take control of the `/etc/ipsec.secrets` file, making it a stub file which links to the l3overlay IPsec secrets located in `/etc/ipsec.l3overlay.secrets`. Also, it will start the IPsec daemon when `l3overlayd` starts, and shut it down with `l3overlayd` when it shuts down.

If `false`, l3overlay will assume that IPsec is being managed elsewhere. In this mode, it will install the IPsec configuration to `l3overlay.conf` under the `/etc/ipsec.d` directory, and stub file will not be installed to `/etc/ipsec.secrets`, instead relying on an existing one to include `/etc/ipsec.l3overlay.secrets`. When starting IPsec, `l3overlayd` will start the IPsec daemon if it is not running, but it will only make sure that its tunnels are started and stopped when `l3overlayd` is being started and stopped, respectively.

Note that if this option is set to `false`, then `l3overlayd` will **NOT** manage IPsec, as it is assumed that the user will want to configure IPsec themselves. A suitable `/etc/ipsec.conf` and `/etc/ipsec.secrets` file **MUST** be provided, which will include the l3overlay IPsec configuration files described above.

Overlay configuration
---------------------

Each overlay to be set up gets its own configuration file, to be located in the `overlays` directory.

### [overlay]

Configuration settings for the overlay, and the mesh tunnels which make the communication channels for the overlay.

#### name
* Type: **name**
* Required: **yes**

The name the overlay will be referred to. Also used to name the network namespace.

#### asn
* Type: **integer**, range 0 <= **asn** <= 65535
* Required: **yes**

The BGP autonomous system (AS) number the overlay will configure the mesh tunnel routing system with.

#### linknet-pool
* Type: **ip network**
* Required: **yes**

The IP network range which can be divided into two-node subnets (`/31` for IPv4, `/127` for IPv6), and then used to address the mesh tunnels in the overlay.

#### this-node
* Type: **name**
* Required: **yes**

The name of the node to configure the overlay for. The name specified here **MUST** be located in the list of nodes, described below.

#### node-*{int}*
* Type: {**name**} {**ip address**}
* Required: **yes**, at least **TWO**

The list of nodes in the mesh, with the Internet-accessible IP address used to build the overlay. A working overlay should have at least two nodes specified here.

The order of the nodes (`node-0`, `node-1`, ...) does not matter significantly, unless new nodes are to be added to the list. New nodes may **ONLY** be appended to the end of the list. This is because if new nodes are added at any other position in the list, it will cause the addresses assigned to mesh tunnel links to change, and l3overlay does not handle this intelligently (it does not ensure the other sides of the tunnel links are changed as well).

#### enabled
* Type: **boolean**
* Required: no

Specifies whether or not this overlay should be configured. The default value is `true`.

#### fwbuilder-script
* Type: **filename** / **filepath**
* Required: no

The location to the fwbuilder script used to build the firewall settings inside the overlay. This can be either an absolute filepath to the script, or simply a filename relative to the `fwbuilder_scripts` directory.

### [static-dummy:*{name}*]

This section is used to define a dummy interface in the overlay.

#### address
* Type: **ip address**
* Required: **yes**

The IP address assigned to the dummy interface.

#### netmask
* Type: **subnet mask**
* Required: **yes**

The subnet mask for the dummy interface address.

### [static-tunnel:*{name}*]

This section is used to define a layer 2/3 GRE tunnel in the overlay. It can be connected to any IP address available in the overlay.

#### mode
* Type: **enum**
* Required: **yes**
* Values: `gre`, `gretap`

The mode in which the GRE tunnel will operate, layer 2 (`gretap`) or layer 3 (`gre`).

#### local
* Type: **ip address**
* Required: **yes**

The local endpoint IP address assigned to the static tunnel.

#### remote
* Type: **ip address**
* Required: **yes**

The remote endpoint IP address assigned to the static tunnel.

#### address
* Type: **ip address**
* Required: **yes**

The IP address assigned to the static tunnel interface.

#### netmask
* Type: **subnet mask**
* Required: **yes**

The subnet mask for the static tunnel interface address.

#### link
* Type: **integer**
* Required: **yes**, **IF** there is more than one tunnel using the address pair

The unique link number for this static tunnel. Required when there is more than one tunnel using the address pair (`local`, `remote`). Checks are run on all GRE/GRETAP tunnel interfaces created by l3overlay to assert this requirement.

### [static-tuntap:*{name}*]

This section is used to define a TUN or TAP virtual interface in the overlay.

#### mode
* Type: **enum**
* Required: **yes**
* Values: `tun`, `tap`

The mode in which the virtual interface will operate.

#### address
* Type: **ip address**
* Required: **yes**

The IP address assigned to the virtual interface.

#### netmask
* Type: **subnet mask**
* Required: **yes**

The subnet mask for the virtual interface address.

#### uid
* Type: **integer**
* Required: no

The user ID which owns and is allowed to attach to the 'network/wire' side of the interface.

#### gid
* Type: **integer**
* Required: no

The group ID which is allowed to attach to the 'network/wire' side of the interface.

### [static-vlan:*{name}*]

This section is used to statically define a IEEE 802.1Q VLAN interface, assigned to a physical interface, which will be accessible in the overlay via a veth pair.

#### id
* Type: **integer**
* Required: **yes**

The IEEE 802.1Q VLAN ID tag for the static VLAN interface.

#### physical-interface
* Type: **name**
* Required: **yes**

The physical interface assigned to the static VLAN interface.

#### address
* Type: **ip address**
* Required: **yes**

The IP address assigned to the static VLAN interface.

#### netmask
* Type: **subnet mask**
* Required: **yes**

The subnet mask for the VLAN interface address.

### [static-veth:*{name}*]

This section is used to configure a static veth pair, with an inner interface inside the overlay, and an outer interface, either in the root namespace, or an externally created network namespace.

#### inner-address|outer-address
* Type: **ip address**
* Required: no

The IP address assigned to the either the inner interface inside the overlay, or the outer interface in the root namespace.

In a veth pair, only one of the two interfaces should be configured. Therefore, either `inner-address` or `outer-address` can be specified, but not both at the same time.

However, if `inner-interface-bridged` is set to `true`, the inner interface will be bridged to a dummy interface, allowing both `inner-address` and `outer-address` to be used.

If both are specified, they must both be the same type of IP address. In other words, both must be IPv4, or both must be IPv6, but not a mix of IPv4 and IPv6.

#### netmask
* Type: **subnet mask**
* Required: **yes**, **IF** `inner-address` or `outer-address` is defined

The subnet mask for the assigned address. If both `inner-address` and `outer-address` are defined with the help of `inner-interface-bridged`, this option will be used as the netmask value for both of them, as they should be part of the same subnet. 

#### inner-namespace
* Type: **name**
* Required: no

The name of the network namespace to move the inner interface into. The network namespace will be created if it does not already exist, but it will not be deleted once the static veth pair is shut down.

This option can also be used to connect two overlays together, via the static veth pair. To link overlays this way, define `inner-namespace` in just one of the overlays. The overlay which the static veth is defined in will get the outer interface, and the overlay specified in `inner-namespace` will get the inner interface.

Note that this does not do any additional configuration to overlays when they are linked via this option, it is simply a veth pair. To allow traffic to flow in the veth pair, additional work needs to be done.

For a fully configured and routed link between overlays, consider using a `[static-overlay-link]`.

#### outer-interface-bridged
* Type: **boolean**
* Required: no

Attaches the outer interface of the static veth to a bridge interface, along with a dummy interface. This allows both `inner-address` and `outer-address` to be used at the same time.

With this option set, `inner-address` goes to the inner interface as normal, but `outer-address` will be assigned to the bridge interface rather than being directly assigned to the inner interface.

### [static-overlay-link:*{name}*]

This section is used to create a link between two overlays, by creating a veth pair between them. The outer veth interface stays in the creating overlay, and gets bridged to a dummy interface, and the inner veth interface gets moved to the overlay to be linked to. A BGP peering is also set up between them, allowing route distribution to take place between the overlays.

#### outer-address
* Type: **ip address**
* Required: **yes**

The IP address assigned to the bridge interface in this overlay, to address the link between the two overlays. This must be the same type of IP address as the value set in `inner-address`.

#### inner-address
* Type: **ip address**
* Required: **yes**

The IP address assigned to the veth interface in the opposing connected overlay, to address the link between the two overlays. This must be the same type of IP address as the value set in `outer-address`.

#### inner-overlay-name
* Type: **name**
* Required: **yes**

The name of the overlay to link with.

#### netmask
* Type: **subnet mask**
* Required: **yes**

The subnet mask for the assigned addresses. Usually this would be set to `31`/`255.255.255.254` (IPv4) or `127` (IPv6) to configure the link as a two-node subnet.

### [static-bgp:*{name}*]

This section is used to define a static BGP protocol in the BIRD routing daemon, used for distributing routes in the overlay. This is made to be used in conjunction with static GRE tunnels, to distribute routes across it.

#### neighbor
* Type: **ip address**
* Required: **yes**

The neighbour BGP node's IP address.

#### local
* Type: **ip address**
* Required: no

The local IP address used to make the BGP connection with the neighbour. Optional.

#### local-asn
* Type: **integer**, range 0 <= **local-asn** <= 65535
* Required: no

The BGP autonomous system (AS) number used to identify the AS the local node is part of. The default value is the ASN number set for the overlay (the `asn` value in the `[overlay]` section).

#### neighbor-asn
* Type: **integer**, range 0 <= **neighbor-asn** <= 65535
* Required: no

The BGP autonomous system (AS) number used to identify the AS the neighbour node is part of.  The default value is the ASN number set for the overlay (the `asn` value in the `[overlay]` section).

#### bfd
* Type: **boolean**
* Required: no

Enable BFD for the BGP protocol, to monitor for neighbour availability and failure detection. Note that BFD also needs to be supported by the neighbour. Defaults to `false`.

#### ttl-security
* Type: **boolean**
* Required: no

Enable the RFC 5082 TTL security mechanism on this BGP protocol. Also needs to be enabled by the neighbour. Defaults to `false`.

#### description
* Type: **string**
* Required: no

An optional description of the BGP protocol, displayed with the use of `show protocol all` in the BIRD client.

#### import-prefix[-*{int}*]
* Type: **bird prefix**
* Required: no

One or more BIRD filters used to filter the routes which get imported into the BGP protocol. The default is to import all routes.

See the [BIRD filter documentation on data types](http://bird.network.cz/?get_doc&f=bird-5.html#ss5.2) for more information.
