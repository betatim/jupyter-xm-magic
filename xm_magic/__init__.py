#!/usr/bin/env python
from __future__ import absolute_import
import os.path
import sys
import warnings


from.sigplot import SigPlot

from IPython.display import (
    display,
    Javascript
)
from notebook import nbextensions

try:
    from XMinter import xm as _xm
except ImportError:
    _xm = None

try:
    import bluefile
except ImportError:
    bluefile = None

__version__ = '0.0.1'


def prepare_js():
    pkgdir = os.path.dirname(__file__)
    sigplotdir = os.path.join(pkgdir, 'sigplotjs')
    nbextensions.install_nbextension(sigplotdir, user=True, overwrite=True)
    display(Javascript("utils.load_extensions('sigplotjs/widget_sigplot');"))

def load_ipython_extension(ipython):
    if sys.version_info[0] == 3:
        warnings.warn ("bluefile and xm extensions not supported by Python 3; functionality will be limited")

    if bluefile is None:
        warnings.warn("Cannot import 'bluefile', functionality may be limited")

    prepare_js()

    ipython.push("SigPlot")


def unload_ipython_extension(ipython):
    pass
