#!/usr/bin/make -f
# -*- makefile -*-


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

# l3overlay - IPsec overlay network manager
# Makefile  - Build system


##############################


#
# Makefile arguments
# ------------------
#
# Any of the parameters in this Makefile can be overridden on the command line.
# Some variables are designed to be used like this, to provide optional
# parameters.
#
# Use them like so:
#   $ make install <KEY>=<VALUE>
#


##############################


#
## Build system parameters.
#

# Parameters that can be changed.
ifdef VIRTUALENV
PREFIX = $(VIRTUALENV)
else
PREFIX = /usr/local
endif

INSTALL_SCRIPTS = $(PREFIX)/sbin

# Constants that should not be changed, except for when using
# template installation targets.
CONFIG_DIR = $(VIRTUALENV)/etc/l3overlay

# Template file variable list.
PARAMS = PREFIX INSTALL_SCRIPTS CONFIG_DIR


##############################


#
## setup.py parameters.
#

ifdef PREFIX
SETUP_PY_PREFIX = --prefix=$(PREFIX)
endif

ifdef INSTALL_SCRIPTS
SETUP_PY_INSTALL_SCRIPTS = --install-scripts=$(INSTALL_SCRIPTS)
endif

ifdef INSTALL_DATA
SETUP_PY_INSTALL_DATA = --install-data=$(INSTALL_DATA)
endif

ifdef INSTALL_LIB
SETUP_PY_INSTALL_LIB = --install-lib=$(INSTALL_LIB)
endif


##############################


#
## Build system files and directories.
#

SETUP_PY            = setup.py
TEMPLATE_PROCESS_PY = template_process.py

SRC_DIR    = src
MODULE_DIR = $(SRC_DIR)/l3overlay

TESTS_BIN_DIR = tests/tests
TESTS_SRC_DIR = tests


##############################


#
## Commands.
#

# Detect usable Python command, if not defined by the user.
ifndef PYTHON
PYTHON_MAJOR_VER = $(shell python3 -V | sed 's:^Python \([0-9][0-9]*\)\..*$$:\1:')
PYTHON_MINOR_VER = $(shell python3 -V | sed 's:^Python [0-9][0-9]*\.\([0-9][0-9]*\)\..*$$:\1:')
ifeq ($(shell test $(PYTHON_MAJOR_VER) -eq 3 -a $(PYTHON_MINOR_VER) -ge 4 && echo true), true)
PYTHON = $(shell which python3)
endif
endif

ifndef PYTHON
PYTHON = $(shell which python3.5)
endif

ifndef PYTHON
PYTHON = $(shell which python3.4)
endif

ifndef PYTHON
$(error l3overlay only supports Python >= 3.4.0)
endif

# Python tools.
PYLINT = pylint
PIP = pip3
# An alternative to this if the default doesn't work:
# PIP = $(PYTHON) -m pip

# System commands.
FIND    = find
INSTALL = install
RM      = rm -f
RMDIR   = rm -rf


##############################


#
## Targets.
#

all:
	@echo "l3overlay make targets:"
	@echo "  lint - run pylint code quality check"
	@echo "  test - run unit tests"
	@echo
	@echo "  sdist - build Python source distribution"
	@echo "  bdist_wheel - build Python binary wheel distribution"
	@echo
	@echo "  install - build and install to local system"
	@echo "  sysv-install - generate and install a SysV init script"
	@echo "  upstart-install - generate and install an Upstart configuration"
	@echo
	@echo "  uninstall - uninstall from local system"
	@echo "  clean - clean build files"
	@echo "See 'Makefile' for more details."


lint:
	$(PYLINT) $(MODULE_DIR)


test:
	@for t in $(shell $(FIND) $(TESTS_BIN_DIR) -maxdepth 1 -name 'test_*.py'); do \
		PYTHONPATH=$(TESTS_SRC_DIR):$(SRC_DIR) $(PYTHON) $$t || exit $$?; \
	done


sdist:
	$(PYTHON) $(SETUP_PY) sdist


bdist_wheel:
	$(PYTHON) $(SETUP_PY) bdist_wheel


install:
	$(PYTHON) $(SETUP_PY) install $(SETUP_PY_PREFIX) $(SETUP_PY_INSTALL_LIB) $(SETUP_PY_INSTALL_SCRIPTS) $(SETUP_PY_INSTALL_DATA)


%: %.in .FORCE
	$(PYTHON) $(TEMPLATE_PROCESS_PY) $< $@ $(foreach KEY,$(PARAMS),$(KEY)=$($(KEY)))

default-install: default/l3overlay
	$(INSTALL) -m 644 default/l3overlay $(PREFIX)/etc/default/l3overlay

sysv-install: default-install init.d/l3overlay
	$(INSTALL) -m 755 init.d/l3overlay $(PREFIX)/etc/init.d/l3overlay

upstart-install: default-install upstart/l3overlay.conf
	$(INSTALL) -m 644 upstart/l3overlay.conf $(PREFIX)/etc/init/l3overlay.conf


uninstall:
	$(PIP) uninstall -y l3overlay


clean:
	$(RM) $(CONFIG)
	$(RM) default/l3overlay
	$(RM) init.d/l3overlay
	$(RM) upstart/l3overlay.conf
	$(RMDIR) .tests
	$(RMDIR) build
	$(RMDIR) dist
	$(RMDIR) src/l3overlay.egg-info
	for d in $(shell $(FIND) -name '__pycache__'); do \
		$(RMDIR) $$d; \
	done


.FORCE:

.PHONY: all lint test sdist bdist_wheel install default-install sysv-install upstart-install uninstall clean .FORCE
