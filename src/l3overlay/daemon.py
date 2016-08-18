#
# IPsec overlay network manager (l3overlay)
# l3overlay/daemon.py - daemon thread class
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


import os
import pyroute2
import re
import sys

from l3overlay import overlay
from l3overlay import util

from l3overlay.overlay.interface.overlay_link import OverlayLink
from l3overlay.overlay.interface.veth import VETH

from l3overlay.process import ipsec as ipsec_process

from l3overlay.util import logger

from l3overlay.util.worker import Worker


class Daemon(Worker):
    '''
    Daemon class for overlay management.
    '''

    def __init__(self, dry_run, logger,
            log, log_level, use_ipsec, ipsec_manage, ipsec_psk,
            lib_dir, overlay_dir,
            fwbuilder_script_dir, overlay_conf_dir, template_dir,
            pid, ipsec_conf, ipsec_secrets,
            overlays):
        '''
        Set up daemon internal fields.
        '''

        super().__init__()

        self.dry_run = dry_run
        self.logger = logger

        self.log = log
        self.log_level = log_level

        self.use_ipsec = use_ipsec
        self.ipsec_manage = ipsec_manage
        self.ipsec_psk = ipsec_psk

        self.lib_dir = lib_dir
        self.overlay_dir = overlay_dir
        self.fwbuilder_script_dir = fwbuilder_script_dir
        self.overlay_conf_dir = overlay_conf_dir
        self.template_dir = template_dir

        self.pid = pid
        self.ipsec_conf = ipsec_conf
        self.ipsec_secrets = ipsec_secrets

        self.overlays = overlays.copy()


    def setup(self):
        '''
        Set up daemon runtime state.
        '''

        if self.is_setup():
            raise RuntimeError("daemon setup twice")

        self._gre_keys = {}
        self._interface_names = set()

        self.mesh_links = set()
        self.root_ipdb = pyroute2.IPDB()

        for o in self.overlays_list_sorted():
            try:
                o.setup(self)
            except Exception as e:
                o.logger.exception(e)
                sys.exit(1)

        self.ipsec_process = ipsec_process.create(self)

        self.set_setup()


    def overlays_list_sorted(self):
        '''
        Resolve inter-overlay dependencies, and place a sorted list
        of overlays, where there would be no dependency issues upon
        starting them, in place of the existing list.
        '''

        os = self.overlays.copy()
        sos = []

        while os:
            Daemon._overlays_list_sorted(os, sos, os.pop(sorted(os.keys())[0]))

        return sos


    @staticmethod
    def _overlays_list_sorted(os, sos, o):
        '''
        Recursive helper method to overlays_list_sorted.
        '''

        for i in o.interfaces:
            if isinstance(i, VETH) and i.inner_namespace in os:
                Daemon._overlays_list_sorted(os, sos, os.pop(i.inner_namespace))
            elif isinstance(i, OverlayLink):
                Daemon._overlays_list_sorted(os, sos, os.pop(i.inner_overlay_name))

        sos.append(o)


    def start(self):
        '''
        Start the daemon.
        '''

        if self.is_starting() or self.is_started():
            raise RuntimeError("daemon started twice")

        self.set_starting()

        self.logger.debug("creating lib dir '%s'" % self.lib_dir)
        util.directory_create(self.lib_dir)

        for o in self.overlays_list_sorted():
            try:
                o.start()
            except Exception as e:
                o.logger.exception(e)
                sys.exit(1)

        self.ipsec_process.start()

        self.set_started()


    def stop(self):
        '''
        Stop the daemon.
        '''

        if not self.is_started():
            raise RuntimeError("daemon not yet started")

        if self.is_stopped() or self.is_stopped():
            raise RuntimeError("daemon stopped twice")

        self.set_stopping()

        self.ipsec_process.stop()
        self.ipsec_process.remove()

        for o in reversed(self.overlays_list_sorted()):
            try:
                o.stop()
            except Exception as e:
                o.logger.exception(e)
                sys.exit(1)
            o.remove()

        self.logger.debug("removing lib dir '%s'" % self.lib_dir)
        util.directory_remove(self.lib_dir)

        self.set_stopped()


    def remove(self):
        '''
        Remove the daemon runtime state.
        '''

        if self.is_removed():
            raise RuntimeError("daemon removed twice")

        if not self.is_stopped():
            raise RuntimeError("daemon not yet stopped")

        self.set_removing()

        self.logger.stop()

        self.set_removed()


    def gre_key(self, local, remote):
        '''
        Return a unique (to this daemon) key value for the given
        (local, remote) link.
        '''

        link = (local, remote)

        if link not in self._gre_keys:
            self._gre_keys[link] = len(self._gre_keys)

        return self._gre_keys[link]


    def interface_name(self, name, suffix=None, limit=15):
        '''
        Returns a valid, unique (to this daemon daemon) interface name
        based on the given base name string
        '''

        ifname_num = 0

        while True:
            digits = len(str(ifname_num))

            if suffix:
                ifname_base = "%s%s" % (
                    re.sub("[^A-Za-z0-9]", "", name)[:limit - len(suffix) - digits],
                    suffix,
                )
            else:
                ifname_base = re.sub("[^A-Za-z0-9]", "", name)[:limit - digits]

            ifname = "%s%i" % (ifname_base, ifname_num)

            if ifname not in self._interface_names:
                break

            ifname_num += 1

        self._interface_names.add(ifname)
        return ifname

Worker.register(Daemon)


class ValueReader(object):
    '''
    Helper class for the read() method.
    '''

    def __init__(self, args, config):
        '''
        Set up value reader internal state.
        '''

        self.args = args
        self.config = config


    def get(self, key, default=None):
        '''
        Get a key, and check the argument list and global configuration,
        in that order, for a corresponding value.

        If one is not found, return default.
        '''

        arg_key = key.lower().replace("-", "_")
        config_key = key.lower().replace("_", "-")

        if arg_key in self.args:
            return self.args[arg_key]
        elif self.config and config_key in self.config:
            return self.config[config_key]
        else:
            return default


def read(args):
    '''
    Create a daemon object using the given arguments.
    '''

    # Load the global configuration file (if specified),
    # and create a ValueReader based on that and the given arguments.
    global_conf = args["global_conf"] if "global_conf" in args else None
    global_config = util.config(global_conf)["global"] if global_conf else None

    reader = ValueReader(args, global_config)

    # Get enough configuration to start a logger.
    log = reader.get("log", os.path.join(util.path_root(), "var", "log", "l3overlay.log"))

    log_level = util.enum_get(
        reader.get("log-level", "INFO"),
        ["NOSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )

    # Start the logger.
    lg = logger.create(log, log_level, "l3overlay")
    lg.start()

    # Log exceptions for the rest of the initialisation process.
    try:
        # Get (general) global configuration.
        dry_run = util.boolean_get(reader.get("dry-run", "false"))

        use_ipsec = util.boolean_get(reader.get("use-ipsec", "false"))
        ipsec_manage = util.boolean_get(reader.get("ipsec-manage", "true"))

        _psk = reader.get("ipsec-psk")
        ipsec_psk = util.hex_get_string(_psk, min=6, max=64) if _psk else None

        # Get required directory paths.
        lib_dir = reader.get("lib-dir", os.path.join(util.path_root(), "var", "lib", "l3overlay"))
        overlay_dir = os.path.join(lib_dir, "overlays")

        fwbuilder_script_dir = reader.get("fwbuilder-script-dir", util.path_search("fwbuilder_scripts"))
        overlay_conf_dir = reader.get("overlay-conf-dir", util.path_search("overlays")) if "overlay_conf" not in args else None
        template_dir = reader.get("template-dir", util.path_search("templates"))

        # Get required file paths.
        pid = reader.get("pid", os.path.join(util.path_root(), "var", "run", "l3overlayd.pid"))

        ipsec_conf = reader.get("ipsec-conf", os.path.join(util.path_root(), "etc", "ipsec.d", "l3overlay.conf"))
        ipsec_secrets = reader.get("ipsec-secrets", os.path.join(util.path_root(), "etc", "ipsec.secrets" if ipsec_manage else "ipsec.l3overlay.secrets"))

        # Create a list of all the overlay configuration file paths.
        overlay_confs = []

        if overlay_conf_dir:
            for overlay_conf_file in os.listdir(overlay_conf_dir):
                overlay_conf = os.path.join(overlay_conf_dir, overlay_conf_file)
                if os.path.isfile(overlay_conf):
                   overlay_confs.append(overlay_conf)
        elif args.overlay_conf:
            overlay_confs.extend(args.overlay_conf)
        else:
            raise RuntimeError("no overlay configuration files found")

        # Create the application state for each overlay.
        overlays = {}

        for overlay_conf in overlay_confs:
            o = overlay.read(log, log_level, overlay_conf)
            overlays[o.name] = o

        # Return a set up daemon object.
        return Daemon(
            dry_run, lg,
            log, log_level, use_ipsec, ipsec_manage, ipsec_psk,
            lib_dir, overlay_dir,
            fwbuilder_script_dir, overlay_conf_dir, template_dir,
            pid, ipsec_conf, ipsec_secrets,
            overlays,
        )

    except Exception as e:
        lg.exception(e)
        sys.exit(1)


def write(daemon, global_conf, overlay_conf_dir):
    '''
    Write a daemon's global configuration to the given file,
    and overlay configurations to the given directory.
    '''

    global_config = util.config()

    global_config["log"] = daemon.log
    global_config["log-level"] = daemon.log_level

    global_config["use-ipsec"] = str(daemon.use_ipsec).lower()
    global_config["ipsec-manage"] = str(daemon.ipsec_manage).lower()
    global_config["ipsec-psk"] = daemon.ipsec_psk

    global_config["lib-dir"] = daemon.lib_dir
    global_config["overlay-dir"] = daemon.overlay_dir

    global_config["fwbuilder-script-dir"] = daemon.fwbuilder_script_dir
    if daemon.overlay_conf_dir:
        global_config["overlay-conf-dir"] = daemon.overlay_conf_dir
    global_config["template-dir"] = daemon.template_dir

    global_config["ipsec-conf"] = daemon.ipsec_conf
    global_config["ipsec-secrets"] = daemon.ipsec_secrets

    global_config.write(global_conf)

    for o in daemon.overlays.values():
        overlay_config = util.config()
        o.write(overlay_config)
        overlay_config.write(os.path.join(overlay_conf_dir, "%s.conf" % o.name))
