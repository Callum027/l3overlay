#
# IPsec overlay network manager (l3overlay)
# l3overlay/util/logger.py - logger class and functions
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


import logging
import os

from l3overlay import util

from l3overlay.util.worker import Worker


class Logger(Worker):
    '''
    Logger.
    '''

    def __init__(self, log, log_level, logger_name, logger_section=None):
        '''
        Set up the logger runtime state.
        '''

        super().__init__()

        self.log = log
        self.log_level = log_level
        self.logger_name = logger_name
        self.logger_section = logger_section

        self.name = "%s-%s" % (logger_name, logger_section) if logger_section else logger_name

        lf = str.format(
            "%(asctime)s {0}: <{1}> [%(levelname)s] %(message)s",
             logger_name,
             logger_section,
        ) if logger_section else "%(asctime)s %(name)s: [%(levelname)s] %(message)s"

        self.logger_formatter = logging.Formatter(lf)

        if self.log:
            util.directory_create(os.path.dirname(self.log))
            self.logger_file_handler = logging.FileHandler(self.log)
            self.logger_file_handler.setFormatter(self.logger_formatter)


    def start(self):
        '''
        Start the logger.
        '''

        if self.is_starting() or self.is_started():
            raise RuntimeError("daemon started twice")

        self.set_starting()

        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.log_level)

        if self.log:
            self.logger.addHandler(self.logger_file_handler)

        self.logger.debug("started logger")

        self.set_started()


    def stop(self):
        '''
        Stop the logger.
        '''

        if not self.is_started():
            raise RuntimeError("logger '%s' not yet started" % self.name)

        if self.is_stopped() or self.is_stopped():
            raise RuntimeError("daemon '%s' stopped twice" % self.name)

        self.set_stopping()

        self.logger.debug("stopping logger")
        if self.log:
            self.logger.removeHandler(self.logger_file_handler)

        self.set_stopped()


    def debug(self, msg, *args, **kwargs):
        '''
        Debug output to the logger.
        '''

        if not self.is_started():
            raise RuntimeError("logger '%s' not yet started" % self.name)

        self.logger.debug(msg, *args, **kwargs)


    def info(self, msg, *args, **kwargs):
        '''
        Info output to the logger.
        '''

        if not self.is_started():
            raise RuntimeError("logger '%s' not yet started" % self.name)

        self.logger.info(msg, *args, **kwargs)


    def warning(self, msg, *args, **kwargs):
        '''
        Warning output to the logger.
        '''

        if not self.is_started():
            raise RuntimeError("logger '%s' not yet started" % self.name)

        self.logger.warning(msg, *args, **kwargs)


    def error(self, msg, *args, **kwargs):
        '''
        Error output to the logger.
        '''

        if not self.is_started():
            raise RuntimeError("logger '%s' not yet started" % self.name)

        self.logger.error(msg, *args, **kwargs)


    def critical(self, msg, *args, **kwargs):
        '''
        Critical output to the logger.
        '''

        if not self.is_started():
            raise RuntimeError("logger '%s' not yet started" % self.name)

        self.logger.critical(msg, *args, **kwargs)


    def log(self, lvl, msg, *args, **kwargs):
        '''
        Log output of a given level to the logger.
        '''

        if not self.is_started():
            raise RuntimeError("logger '%s' not yet started" % self.name)

        self.logger.log(lvl, msg, *args, **kwargs)


    def exception(self, msg, *args, **kwargs):
        '''
        Exception output to the logger.
        '''

        if not self.is_started():
            raise RuntimeError("logger '%s' not yet started" % self.name)

        self.logger.exception(msg, *args, **kwargs)

Worker.register(Logger)


def create(log, log_level, logger_name, logger_section=None):
    '''
    Create a logger.
    '''

    return Logger(log, log_level, logger_name, logger_section)
