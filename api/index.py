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
from urllib.parse import urlparse

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
    
    def _build_wsgi_environ(self, request_method, wsgi_input):
        """
        Build a WSGI environ dictionary from the HTTP request.
        
        Args:
            request_method: HTTP method (GET, POST, etc.)
            wsgi_input: File-like object for request body
            
        Returns:
            WSGI environ dictionary
        """
        parsed_url = urlparse(self.path)
        
        # Parse Host header for server name and port
        host_header = self.headers.get('Host', 'localhost:80')
        if ':' in host_header:
            server_name, server_port = host_header.rsplit(':', 1)
            # Validate port is numeric, default to 80 if not
            try:
                int(server_port)
            except ValueError:
                server_port = '80'
        else:
            server_name = host_header
            server_port = '80'
        
        environ = {
            'REQUEST_METHOD': request_method,
            'SCRIPT_NAME': '',
            'PATH_INFO': parsed_url.path or '/',
            'QUERY_STRING': parsed_url.query or '',
            'CONTENT_TYPE': self.headers.get('Content-Type', ''),
            'CONTENT_LENGTH': self.headers.get('Content-Length', '0'),
            'SERVER_NAME': server_name,
            'SERVER_PORT': server_port,
            'SERVER_PROTOCOL': self.request_version,
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https' if self.headers.get('X-Forwarded-Proto') == 'https' else 'http',
            'wsgi.input': wsgi_input,
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
        
        return environ
    
    def _handle_wsgi_request(self, environ):
        """
        Execute the WSGI application and send the response.
        
        Args:
            environ: WSGI environ dictionary
        """
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
            
            # Send response status - parse status code safely
            status_code = 200  # default
            if self.response_status:
                try:
                    status_code = int(self.response_status.split(' ', 1)[0])
                except (ValueError, IndexError):
                    status_code = 200  # fallback to 200 if parsing fails
            
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
    
    def do_GET(self):
        """
        Handle GET requests by converting them to WSGI format and calling the application.
        """
        environ = self._build_wsgi_environ('GET', io.BytesIO())
        self._handle_wsgi_request(environ)
    
    def do_POST(self):
        """
        Handle POST requests by converting them to WSGI format and calling the application.
        """
        # Read POST data - safely parse Content-Length
        try:
            content_length = int(self.headers.get('Content-Length', 0))
        except (ValueError, TypeError):
            content_length = 0
        
        post_data = self.rfile.read(content_length) if content_length > 0 else b''
        
        environ = self._build_wsgi_environ('POST', io.BytesIO(post_data))
        self._handle_wsgi_request(environ)
    
    def log_message(self, format, *args):
        """
        Override to suppress default logging or customize it.
        """
        # Optionally log to stderr or suppress entirely
        pass


# For backward compatibility, also expose the WSGI application
app = application
