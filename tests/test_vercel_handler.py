#!/usr/bin/env python3
"""
Test the Vercel handler to ensure it doesn't trigger the issubclass() bug.

This test simulates what Vercel's Python runtime does when inspecting the handler:
1. Import the handler module
2. Check that 'handler' exists and is callable
3. Inspect handler.__globals__ for classes that inherit from BaseHTTPRequestHandler
4. Execute the handler with a sample WSGI environ

The original error was:
  TypeError: issubclass() arg 1 must be a class
  at /var/task/vc__handler__python.py:463

This occurred because Vercel's runtime found WSGIRequestHandlerRequestUri
(which inherits from BaseHTTPRequestHandler) in the handler's __globals__.
"""

import sys
import os
import io
from http.server import BaseHTTPRequestHandler

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_handler_globals_isolation():
    """Test that handler.__globals__ doesn't contain BaseHTTPRequestHandler subclasses."""
    # Import the handler module
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'index',
        os.path.join(os.path.dirname(__file__), '..', 'api', 'index.py')
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Check handler exists and is callable
    assert hasattr(module, 'handler'), "Module should have 'handler' attribute"
    handler = module.handler
    assert callable(handler), "handler should be callable"
    
    # Check handler's __globals__ for problematic classes
    problematic_classes = []
    for name, obj in handler.__globals__.items():
        if isinstance(obj, type):  # It's a class
            try:
                if issubclass(obj, BaseHTTPRequestHandler):
                    problematic_classes.append((name, obj))
            except TypeError as e:
                raise AssertionError(
                    f"TypeError when checking {name}: {e}. "
                    "This is the Vercel bug we're trying to avoid!"
                )
    
    assert not problematic_classes, (
        f"Found {len(problematic_classes)} classes inheriting from BaseHTTPRequestHandler "
        f"in handler.__globals__: {[name for name, _ in problematic_classes]}. "
        "This would trigger Vercel's issubclass() bug!"
    )
    
    print("✓ handler.__globals__ is properly isolated")


def test_handler_execution():
    """Test that the handler actually works."""
    from api.index import handler
    
    # Create minimal WSGI environ with proper wsgi.input
    environ = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/',
        'QUERY_STRING': '',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '8000',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'http',
        'wsgi.input': io.BytesIO(),  # Proper WSGI input stream
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }
    
    response_status = []
    response_headers = []
    
    def start_response(status, headers, exc_info=None):
        response_status.append(status)
        response_headers.extend(headers)
        return lambda x: None
    
    # Execute handler
    result = handler(environ, start_response)
    
    # Verify response
    assert response_status, "start_response should have been called"
    assert response_status[0].startswith('200') or response_status[0].startswith('404'), \
        f"Expected 200 or 404 status, got: {response_status[0]}"
    assert response_headers, "Response should have headers"
    assert result is not None, "Handler should return a result"
    
    print(f"✓ handler executed successfully with status: {response_status[0]}")


def test_app_variable():
    """Test that the 'app' variable is properly exposed."""
    from api.index import app, application
    
    # Verify app exists and is the same as application
    assert app is not None, "app should be defined"
    assert app is application, "app should be the same object as application"
    assert callable(app), "app should be callable (WSGI application)"
    
    print("✓ 'app' variable is properly exposed")


if __name__ == '__main__':
    print("Testing Vercel handler isolation fix...")
    print("=" * 60)
    
    try:
        test_handler_globals_isolation()
        test_handler_execution()
        test_app_variable()
        
        print("=" * 60)
        print("✓ ALL TESTS PASSED")
        print("\nThe handler should work correctly on Vercel!")
    except AssertionError as e:
        print("=" * 60)
        print(f"✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print("=" * 60)
        print(f"✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
