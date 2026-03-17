import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Use absolute paths to ensure the module under test is importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Mocking modules that might be missing in the environment
def setup_mocks():
    # Clear sys.modules for these if they are already there from other imports
    for module in ['serial', 'serial.tools', 'serial.tools.list_ports', 'websockets', 'tkinter', 'tkinter.ttk', 'tkinter.scrolledtext']:
        if module in sys.modules:
            del sys.modules[module]

    sys.modules['serial'] = MagicMock()
    sys.modules['serial.tools'] = MagicMock()
    sys.modules['serial.tools.list_ports'] = MagicMock()
    sys.modules['websockets'] = MagicMock()
    # Mock tkinter since it's used in the module
    sys.modules['tkinter'] = MagicMock()
    sys.modules['tkinter.ttk'] = MagicMock()
    sys.modules['tkinter.scrolledtext'] = MagicMock()

setup_mocks()

from udp_to_serial import TCodeWSServer

class TestTCodeWSServer(unittest.TestCase):
    @patch('udp_to_serial.websockets.serve')
    @patch('udp_to_serial.asyncio.new_event_loop')
    @patch('udp_to_serial.asyncio.set_event_loop')
    def test_server_binding_default(self, mock_set_loop, mock_new_loop, mock_ws_serve):
        """Test that the server binds to 127.0.0.1 by default (after fix)"""
        mock_loop = MagicMock()
        mock_new_loop.return_value = mock_loop
        # Make run_until_complete return immediately
        mock_loop.run_until_complete.return_value = MagicMock()
        # Make run_forever raise a dummy exception to break out of the loop
        mock_loop.run_forever.side_effect = Exception("Stop loop")

        # After fix, this should bind to 127.0.0.1 by default
        server = TCodeWSServer(port=8765)
        try:
            server._start_server()
        except Exception as e:
            if str(e) != "Stop loop":
                raise e

        # Before fix, this will fail because it's called with "0.0.0.0"
        # and server doesn't even have a host parameter in __init__ yet.
        mock_ws_serve.assert_called_with(server._handler, "127.0.0.1", 8765)

    @patch('udp_to_serial.websockets.serve')
    @patch('udp_to_serial.asyncio.new_event_loop')
    @patch('udp_to_serial.asyncio.set_event_loop')
    def test_server_binding_configurable(self, mock_set_loop, mock_new_loop, mock_ws_serve):
        """Test that the server binding is configurable (after fix)"""
        mock_loop = MagicMock()
        mock_new_loop.return_value = mock_loop
        mock_loop.run_until_complete.return_value = MagicMock()
        mock_loop.run_forever.side_effect = Exception("Stop loop")

        # After fix, __init__ should accept host
        server = TCodeWSServer(port=8888, host="192.168.1.5")
        try:
            server._start_server()
        except Exception as e:
            if str(e) != "Stop loop":
                raise e

        mock_ws_serve.assert_called_with(server._handler, "192.168.1.5", 8888)

if __name__ == '__main__':
    unittest.main()
