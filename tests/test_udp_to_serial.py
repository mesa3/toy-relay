import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ensure the current directory is in the path to import udp_to_serial
sys.path.append(os.getcwd())

from udp_to_serial import UdpToSerialRelay

class TestUdpToSerialRelay(unittest.TestCase):
    def setUp(self):
        # Initial setup for each test
        self.udp_ip = "127.0.0.1"
        self.udp_port = 8000
        self.serial_port = "COM1"
        self.baud_rate = 115200
        self.relay = UdpToSerialRelay(self.udp_ip, self.udp_port, self.serial_port, self.baud_rate, dummy=True)

    def test_initialization(self):
        """Test if the relay initializes with correct parameters"""
        self.assertEqual(self.relay.udp_ip, self.udp_ip)
        self.assertEqual(self.relay.udp_port, self.udp_port)
        self.assertEqual(self.relay.serial_port_name, self.serial_port)
        self.assertEqual(self.relay.baud_rate, self.baud_rate)
        self.assertTrue(self.relay.dummy)

    @patch('udp_to_serial.socket.socket')
    @patch('udp_to_serial.serial.Serial')
    def test_setup_connections(self, mock_serial, mock_socket):
        """Test connection setup logic"""
        # Create a non-dummy relay for this test
        relay = UdpToSerialRelay(self.udp_ip, self.udp_port, self.serial_port, self.baud_rate, dummy=False)
        
        # Configure mocks
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        
        mock_ser_instance = MagicMock()
        mock_serial.return_value = mock_ser_instance
        
        relay.setup_connections()
        
        # Verify socket setup
        mock_socket.assert_called()
        mock_sock_instance.bind.assert_called_with((self.udp_ip, self.udp_port))
        mock_sock_instance.setblocking.assert_called_with(False)
        
        # Verify serial setup
        mock_serial.assert_called_with(
            port=self.serial_port,
            baudrate=self.baud_rate,
            timeout=0.01,
            write_timeout=0.1
        )
        # Check initial command sent
        mock_ser_instance.write.assert_called()

    def test_process_tcode_buffer_merging(self):
        """Test the logic for merging multiple T-Code packets"""
        packets = [
            b"L0000\n",
            b"L1500 I100\n",
            b"L0999\n",  # Should overwrite L0000
            b"R1200\n"
        ]
        
        result = self.relay.process_tcode_buffer(packets)
        
        # We expect a string containing L0999, L1500I100, R1200
        # The order depends on dictionary iteration order, so we check for presence
        self.assertIn("L0999", result)
        self.assertIn("L1500I100", result)
        self.assertIn("R1200", result)
        self.assertTrue(result.endswith("\n"))
        
        # L0000 should NOT be in the result (it was overwritten)
        self.assertNotIn("L0000 ", result) 

    def test_process_tcode_buffer_mixed_garbage(self):
        """Test parsing with mixed valid and invalid data"""
        packets = [
            b"GARBAGE",
            b"L0500",
            b"InvalidAxis999",
            b"V0200"
        ]
        
        result = self.relay.process_tcode_buffer(packets)
        
        self.assertIn("L0500", result)
        self.assertIn("V0200", result)

    def test_process_tcode_buffer_empty(self):
        """Test with empty input"""
        result = self.relay.process_tcode_buffer([])
        self.assertIsNone(result)

    def test_process_tcode_v03_format(self):
        """Test v0.3 extended range and axes"""
        packets = [b"A05000\n", b"L09999 I200\n"]
        result = self.relay.process_tcode_buffer(packets)
        
        self.assertIn("A05000", result)
        self.assertIn("L09999I200", result)

if __name__ == '__main__':
    unittest.main()