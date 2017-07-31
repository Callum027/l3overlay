#
# IPsec overlay network manager (l3overlay)
# l3overlay/l3overlay_birdc.py - l3overlay-birdc helper script
#
# Copyright (c) 2017 Catalyst.net Ltd
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


import argparse
import os

from l3overlay import util


def main():
    '''
    l3overlay overlay-specific birdc wrapper.
    '''

    # Find birdc command. Fails if it is not available.
    birdc = util.command_path("birdc")

    # Parse arguments.
    argparser = argparse.ArgumentParser(
        description="l3overlay overlay-specific birdc wrapper.",
        usage="%(prog)s [-h] [-gc FILE] [-Ld DIR] [-6] OVERLAY [BIRDC-ARGS...]",
    )

    argparser.add_argument(
        "-gc", "--global-conf",
        metavar="FILE",
        type=str,
        default=None,
        help="use FILE as the global configuration file",
    )

    argparser.add_argument(
        "-Ld", "--lib-dir",
        metavar="DIR",
        type=str,
        default=None,
        help="use DIR as the runtime data directory (overrides -gc)",
    )

    argparser.add_argument(
        "-6", "--use-bird6",
        action="store_true",
        help="launch birdc for bird6 (default is bird4)",
    )

    argparser.add_argument(
        "overlay_name",
        metavar="OVERLAY",
        type=str,
        help="launch birdc under overlay OVERLAY",
    )

    args, birdc_user_args = argparser.parse_known_args()
    args = vars(args)

    # Process arguments.
    overlay_name = args["overlay_name"]
    use_bird6 = args["use_bird6"]

    if "lib_dir" in args:
        lib_dir = args["lib_dir"]
    else:
        global_conf = args["global_conf"] if "global_conf" in args else util.path_search("global.conf")
        config = util.config(global_conf)["global"] if global_conf else None
        lib_dir = config["lib-dir"] if config and "lib-dir" in config else os.path.join(util.path_root(), "var", "lib", "l3overlay")

    # Build birdc command line arguments.
    birdc_args = ["-c", os.path.join(self.lib_dir, "overlays", overlay_name, "run", "bird", "bird6.ctl" if use_bird6 else "bird.ctl")]
    birdc_args.update(birdc_user_args)

    # Use the exec system call to replace this script with
    # birdc instance directly.
    os.execv(birdc, birdc_args)
