#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of morss
#
# Copyright (C) 2013-2020 pictuga <contact@pictuga.com>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>.

"""
Vercel serverless function entry point for Morss.

This module provides a WSGI-compatible handler for Vercel's Python runtime.
The handler is isolated from morss.wsgi's module-level classes to avoid
triggering Vercel's issubclass() inspection bug.
"""

import sys
import os

# Set up path at module load time (once, not per-request)
_parent_dir = os.path.normpath(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# # Cache for the application - using exec() to completely isolate the import
# _app_cache = {}

# 直接导入，不用 exec 隔离（很多项目都这样成功了）
from morss.wsgi import application

# Vercel 更喜欢看到这个名字
app = application

def handler(environ, start_response):
    """
    WSGI application handler for Vercel.
    
    This handler uses exec() to completely isolate the morss.wsgi module's
    globals from this handler's __globals__, preventing Vercel's Python runtime
    from encountering WSGIRequestHandlerRequestUri and other classes that
    trigger its issubclass() inspection bug.
    
    Why exec() instead of importlib.import_module():
    Using exec() with an isolated namespace allows us to import and extract
    only the 'application' object without adding any imports to this handler's
    __globals__. With importlib, we'd need to import the module which would
    add the import to __globals__, or store a module reference which would
    expose the module's classes. exec() keeps this handler's __globals__ clean.
    
    Args:
        environ: WSGI environment dict
        start_response: WSGI start_response callable
        
    Returns:
        WSGI response iterable
    """
    if 'app' not in _app_cache:
        # Use exec() to import in an isolated namespace
        local_ns = {}
        exec('from morss.wsgi import application', local_ns)
        _app_cache['app'] = local_ns['application']
    
    return _app_cache['app'](environ, start_response)
