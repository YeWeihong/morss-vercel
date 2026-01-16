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
"""

import sys
import os

# Set up path at module load time (once, not per-request)
# This ensures __file__ is available and path is set correctly
_parent_dir = os.path.normpath(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# Import the WSGI application at module level
# Note: We import inside a function wrapper to avoid exposing morss.wsgi's
# module-level objects in the handler's __globals__, which would trigger
# Vercel's issubclass() bug
def _get_application():
    """Lazy import wrapper to isolate morss.wsgi's globals."""
    from morss.wsgi import application
    return application

# Cache the application after first import
_app = None

def handler(environ, start_response):
    """
    WSGI application handler for Vercel.
    
    Args:
        environ: WSGI environment dict
        start_response: WSGI start_response callable
        
    Returns:
        WSGI response iterable
    """
    global _app
    if _app is None:
        _app = _get_application()
    return _app(environ, start_response)
