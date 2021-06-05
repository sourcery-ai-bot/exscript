from builtins import range
import sys
import unittest
import re
import os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from Exscript import Account
from Exscript.account import AccountPool
from Exscript.util.file import get_accounts_from_file


class AccountPoolTest(unittest.TestCase):
    CORRELATE = AccountPool

    def setUp(self):
        self.user1 = 'testuser1'
        self.password1 = 'test1'
        self.account1 = Account(self.user1, self.password1)
        self.user2 = 'testuser2'
        self.password2 = 'test2'
        self.account2 = Account(self.user2, self.password2)
        self.accm = AccountPool()

    def testConstructor(self):
        accm = AccountPool()
        self.assertEqual(accm.n_accounts(), 0)

        accm = AccountPool([self.account1, self.account2])
        self.assertEqual(accm.n_accounts(), 2)

    def testAddAccount(self):
        self.assertEqual(self.accm.n_accounts(), 0)
        self.accm.add_account(self.account1)
        self.assertEqual(self.accm.n_accounts(), 1)

        self.accm.add_account(self.account2)
        self.assertEqual(self.accm.n_accounts(), 2)

    def testReset(self):
        self.testAddAccount()
        self.accm.reset()
        self.assertEqual(self.accm.n_accounts(), 0)

    def testHasAccount(self):
        self.assertEqual(self.accm.has_account(self.account1), False)
        self.accm.add_account(self.account1)
        self.assertEqual(self.accm.has_account(self.account1), True)

    def testGetAccountFromHash(self):
        account = Account('user', 'test')
        thehash = account.__hash__()
        self.accm.add_account(account)
        self.assertEqual(self.accm.get_account_from_hash(thehash), account)

    def testGetAccountFromName(self):
        self.testAddAccount()
        self.assertEqual(self.account2,
                         self.accm.get_account_from_name(self.user2))

    def testNAccounts(self):
        self.testAddAccount()

    def testAcquireAccount(self):
        self.testAddAccount()
        self.accm.acquire_account(self.account1)
        self.account1.release()
        self.accm.acquire_account(self.account1)
        self.account1.release()

        # Add three more accounts.
        filename = os.path.join(os.path.dirname(__file__), 'account_pool.cfg')
        self.accm.add_account(get_accounts_from_file(filename))
        self.assertEqual(self.accm.n_accounts(), 5)

        for _ in range(2000):
            # Each time an account is acquired a different one should be
            # returned.
            acquired = {}
            for _ in range(5):
                account = self.accm.acquire_account()
                self.assertTrue(account is not None)
                self.assertNotIn(account.get_name(), acquired)
                acquired[account.get_name()] = account

            # Release one account.
            acquired['abc'].release()

            # Acquire one account.
            account = self.accm.acquire_account()
            self.assertEqual(account.get_name(), 'abc')

            # Release all accounts.
            for account in list(acquired.values()):
                account.release()

    def testReleaseAccounts(self):
        account1 = Account('foo')
        account2 = Account('bar')
        pool = AccountPool()
        pool.add_account(account1)
        pool.add_account(account2)
        pool.acquire_account(account1, 'one')
        pool.acquire_account(account2, 'two')

        self.assertNotIn(account1, pool.unlocked_accounts)
        self.assertNotIn(account2, pool.unlocked_accounts)
        pool.release_accounts('one')
        self.assertIn(account1, pool.unlocked_accounts)
        self.assertNotIn(account2, pool.unlocked_accounts)
        pool.release_accounts('one')
        self.assertIn(account1, pool.unlocked_accounts)
        self.assertNotIn(account2, pool.unlocked_accounts)
        pool.release_accounts('two')
        self.assertIn(account1, pool.unlocked_accounts)
        self.assertIn(account2, pool.unlocked_accounts)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(AccountPoolTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
