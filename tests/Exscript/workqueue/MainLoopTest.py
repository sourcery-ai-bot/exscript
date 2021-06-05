from builtins import range
import sys
import unittest
import re
import os.path
import threading
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from Exscript.workqueue.mainloop import MainLoop
from Exscript.workqueue.pipeline import Pipeline
from Exscript.workqueue.job import Process


class MainLoopTest(unittest.TestCase):
    def setUp(self):
        pass

    def testMainLoop(self):
        lock = threading.Lock()
        data = {'sum': 0, 'randsum': 0}
        ml = MainLoop(Pipeline(), Process)
        nop = lambda x: None

        for _ in range(12345):
            ml.enqueue(nop, name='test', times=1, data=None)

        self.assertEqual(0, data['sum'])

        # Note: Further testing is done in WorkQueueTest.py


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(MainLoopTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
