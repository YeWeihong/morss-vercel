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
Vercel serverless function entry point for Morss
This module adapts the WSGI application for Vercel's serverless environment
"""

import sys
import os

# Add parent directory to path to import morss module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the WSGI application as 'handler' for Vercel
# Note: Only export 'handler' to avoid Vercel's issubclass() TypeError
# The original code exported 'app', 'application', and 'handler', which
# caused Vercel's runtime inspection code to fail with:
# "TypeError: issubclass() arg 1 must be a class"
from morss.wsgi import application as handler
