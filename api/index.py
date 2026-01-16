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

This module provides a BaseHTTPRequestHandler-based entry point for Vercel's Python runtime.

Vercel's Python runtime expects the handler to be a class that inherits from
http.server.BaseHTTPRequestHandler. This allows Vercel to properly instantiate and
manage the HTTP request handling.
"""

import sys
import os
import io
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Set up Python path to allow importing morss modules
# This is necessary because the morss package is in the parent directory
_parent_dir = os.path.normpath(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# Import the WSGI application from morss.wsgi
# The application is a fully configured WSGI app with all middleware applied
from morss.wsgi import application


class handler(BaseHTTPRequestHandler):
    """
    HTTP request handler for Vercel serverless deployment.
    
    This class inherits from BaseHTTPRequestHandler and bridges between
    Vercel's HTTP server interface and the WSGI application interface used by morss.
    """
    
    def do_GET(self):
        """
        Handle GET requests by converting them to WSGI format and calling the application.
        """
        # Parse the URL
        parsed_url = urlparse(self.path)
        
        # Build WSGI environ dictionary
        environ = {
            'REQUEST_METHOD': 'GET',
            'SCRIPT_NAME': '',
            'PATH_INFO': parsed_url.path or '/',
            'QUERY_STRING': parsed_url.query or '',
            'CONTENT_TYPE': self.headers.get('Content-Type', ''),
            'CONTENT_LENGTH': self.headers.get('Content-Length', '0'),
            'SERVER_NAME': self.headers.get('Host', 'localhost').split(':')[0],
            'SERVER_PORT': self.headers.get('Host', 'localhost:80').split(':')[-1] if ':' in self.headers.get('Host', '') else '80',
            'SERVER_PROTOCOL': self.request_version,
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https' if self.headers.get('X-Forwarded-Proto') == 'https' else 'http',
            'wsgi.input': io.BytesIO(),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': True,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
        }
        
        # Add HTTP headers to environ
        for header, value in self.headers.items():
            header_name = 'HTTP_' + header.upper().replace('-', '_')
            environ[header_name] = value
        
        # Special handling for REQUEST_URI (for compatibility with morss)
        environ['REQUEST_URI'] = self.path
        
        # Response tracking
        self.response_status = None
        self.response_headers = []
        
        def start_response(status, headers, exc_info=None):
            """WSGI start_response callable."""
            self.response_status = status
            self.response_headers = headers
            return lambda data: None  # Write callable (not used in most cases)
        
        try:
            # Call the WSGI application
            response_data = application(environ, start_response)
            
            # Send response status
            status_code = int(self.response_status.split(' ', 1)[0]) if self.response_status else 200
            self.send_response(status_code)
            
            # Send response headers
            for header_name, header_value in self.response_headers:
                self.send_header(header_name, header_value)
            self.end_headers()
            
            # Send response body
            for data in response_data:
                if isinstance(data, bytes):
                    self.wfile.write(data)
                else:
                    self.wfile.write(data.encode('utf-8'))
                    
        except Exception as e:
            # Handle errors gracefully
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def do_POST(self):
        """
        Handle POST requests by converting them to WSGI format and calling the application.
        """
        # Parse the URL
        parsed_url = urlparse(self.path)
        
        # Read POST data
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b''
        
        # Build WSGI environ dictionary
        environ = {
            'REQUEST_METHOD': 'POST',
            'SCRIPT_NAME': '',
            'PATH_INFO': parsed_url.path or '/',
            'QUERY_STRING': parsed_url.query or '',
            'CONTENT_TYPE': self.headers.get('Content-Type', ''),
            'CONTENT_LENGTH': str(content_length),
            'SERVER_NAME': self.headers.get('Host', 'localhost').split(':')[0],
            'SERVER_PORT': self.headers.get('Host', 'localhost:80').split(':')[-1] if ':' in self.headers.get('Host', '') else '80',
            'SERVER_PROTOCOL': self.request_version,
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https' if self.headers.get('X-Forwarded-Proto') == 'https' else 'http',
            'wsgi.input': io.BytesIO(post_data),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': True,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
        }
        
        # Add HTTP headers to environ
        for header, value in self.headers.items():
            header_name = 'HTTP_' + header.upper().replace('-', '_')
            environ[header_name] = value
        
        # Special handling for REQUEST_URI (for compatibility with morss)
        environ['REQUEST_URI'] = self.path
        
        # Response tracking
        self.response_status = None
        self.response_headers = []
        
        def start_response(status, headers, exc_info=None):
            """WSGI start_response callable."""
            self.response_status = status
            self.response_headers = headers
            return lambda data: None  # Write callable (not used in most cases)
        
        try:
            # Call the WSGI application
            response_data = application(environ, start_response)
            
            # Send response status
            status_code = int(self.response_status.split(' ', 1)[0]) if self.response_status else 200
            self.send_response(status_code)
            
            # Send response headers
            for header_name, header_value in self.response_headers:
                self.send_header(header_name, header_value)
            self.end_headers()
            
            # Send response body
            for data in response_data:
                if isinstance(data, bytes):
                    self.wfile.write(data)
                else:
                    self.wfile.write(data.encode('utf-8'))
                    
        except Exception as e:
            # Handle errors gracefully
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def log_message(self, format, *args):
        """
        Override to suppress default logging or customize it.
        """
        # Optionally log to stderr or suppress entirely
        pass


# For backward compatibility, also expose the WSGI application
app = application
