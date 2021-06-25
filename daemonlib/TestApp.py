"""App class test suite."""
import unittest
import os
from app import App, read_config
from multiprocessing import Process


class TestReadConfig(unittest.TestCase):
    """Test the read config function."""

    test_config_file = 'test_cfg.ini'

    def setUp(self):
        """Set up the config file."""
        test_config = "[section1]\n"
        test_config += "test1 = 1\n"
        test_config += "test2 = 2\n"
        test_config += "[section2]\n"
        test_config += "test3 = /var"
        with open(self.test_config_file, 'w') as f:
            f.write(test_config)

    def tearDown(self):
        """Destroy the config file."""
        os.remove(self.test_config_file)

    def testProperConfig(self):
        """Test with a proper config."""
        config = read_config(self.test_config_file)
        self.assertEqual((config['section1']['test1'],
                          config['section1']['test2'],
                          config['section2']['test3']), ('1', '2', '/var'))

    def testNonExistingFile(self):
        """Test without an existing file."""
        config = read_config("non-existing.ini")
        self.assertFalse(config)


if __name__ == '__main__':
    unittest.main()
