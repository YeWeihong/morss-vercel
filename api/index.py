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

This module provides a clean WSGI application entry point for Vercel's Python runtime.

Why this simple approach works:
1. Vercel looks for a variable named "app" or "handler" in the entry point file
2. The problematic WSGIRequestHandlerRequestUri class (which inherits from 
   BaseHTTPRequestHandler) is defined in morss.wsgi, not in this file
3. Vercel's runtime only inspects the entry point file's globals for HTTP handler
   classes, not the globals of imported modules
4. By directly importing and exposing the WSGI application, we keep this file
   simple and avoid the issubclass() inspection issues

Previous attempts using exec() and namespace isolation were overly complex and
still failed because Vercel could detect referenced classes through various means.
The simplest solution is the most reliable.
"""

import sys
import os

# Set up Python path to allow importing morss modules
# This is necessary because the morss package is in the parent directory
_parent_dir = os.path.normpath(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# Import the WSGI application from morss.wsgi
# The application is a fully configured WSGI app with all middleware applied
from morss.wsgi import application

# Expose the application as "app" - this is what Vercel will use
# Vercel's Python runtime prefers finding a variable named "app"
app = application

# Also provide a handler function for compatibility with different Vercel configurations
# This is a simple passthrough to the WSGI application
def handler(environ, start_response):
    """
    WSGI application handler for Vercel.
    
    This is a simple wrapper that delegates to the morss WSGI application.
    Vercel can use either the 'app' variable or this 'handler' function.
    
    Args:
        environ: WSGI environment dict
        start_response: WSGI start_response callable
        
    Returns:
        WSGI response iterable
    """
    return app(environ, start_response)
