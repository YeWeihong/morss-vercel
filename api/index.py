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
The handler uses late-binding imports to avoid exposing module-level classes
from morss.wsgi in the handler's __globals__, which would trigger a bug in
Vercel's runtime where it calls issubclass() on non-class objects.
"""


def handler(environ, start_response):
    """
    WSGI application handler for Vercel.
    
    Args:
        environ: WSGI environment dict
        start_response: WSGI start_response callable
        
    Returns:
        WSGI response iterable
    """
    # Import everything inside the function to keep module namespace minimal
    import sys
    import os
    
    # Add parent directory to path to import morss module
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    
    # Import morss application
    from morss.wsgi import application
    
    return application(environ, start_response)
