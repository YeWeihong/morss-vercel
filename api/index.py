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

IMPORTANT: Why complete isolation from wsgiref.simple_server is critical:

Vercel's Python runtime (/var/task/vc__handler__python.py) inspects the handler module
and checks if any objects in the module's namespace are subclasses of BaseHTTPRequestHandler.
The inspection code looks something like:

    for base in some_collection:
        if not issubclass(base, BaseHTTPRequestHandler):
            ...

The problem occurs at TWO levels:
1. Direct class definitions: If WSGIRequestHandlerRequestUri (which inherits from 
   BaseHTTPRequestHandler) is defined in morss.wsgi, it ends up in the application 
   function's __globals__, causing Vercel's inspection to fail.

2. Module imports: Even if the class is moved, importing wsgiref.simple_server at the
   module level exposes wsgiref.simple_server.WSGIRequestHandler (which also inherits
   from BaseHTTPRequestHandler) through the module namespace, triggering the same error.

The complete solution:
1. WSGIRequestHandlerRequestUri is isolated in morss/server.py
2. wsgiref.simple_server is imported locally within cgi_start_server() only
3. Both the custom class AND the wsgiref.simple_server module are kept out of the
   WSGI application's __globals__
4. Vercel's runtime can safely load and inspect the handler module without encountering
   any BaseHTTPRequestHandler subclasses
5. The application works correctly in both serverless (Vercel) and standalone modes

This approach ensures complete isolation while maintaining full functionality.
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
