from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


# Uses Mocking to test the database.
class CommandsTestCase(TestCase):

    def test_wait_for_db_ready(self):
        # Test to wait for the db to become available.
        # Checks whether an OperationalError is retrieved. If so,
        # then a DB isn't available.
        # We're going to override the ConnectionHandler.
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 1)

    @patch('time.sleep', return_value=None)
    def test_wait_for_db(self, ts):
        # Test to wait for the db. Will check 5 times, and a 6th.

        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # Python unittest module allows you to set a side effect
            # to the function you're mocking.
            # Raises OperationalError 5 times, on the 6th - call completes.
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 6)
