#!/usr/bin/python

"""Tests the heapmanip module.

Usage:
    
    python heapmaniptest.py
"""

import time
import unittest
import heapmanip
import test_heapmanip
from heapcustomlib import *


class Test1(unittest.TestCase, test_heapmanip.MailDBHandler):

    def setUp(self):
        self.setUpDirs()
        self._maildb = self.createMailDB()
        self.create_threadst()

    def test_format_date(self):

        options = date_defopts({'localtime_fun': time.gmtime})
        self.assertEquals(format_date(self._posts[0], options), '(2008.08.20.)')

        options['date_format'] = '%Y.%m.%d. %H:%M:%S'
        self.assertEquals(
            format_date(self._posts[0], options),
            '2008.08.20. 15:41:00')

    def test_create_should_print_date_fun(self):
        # sections
        section = ('', self._maildb.all(), {})
        sections = [section]
        heapmanip.Generator.sections_setdefaultoptions(sections)

        # date options
        options = date_defopts({'maildb': self._maildb,
                                'timedelta': datetime.timedelta(seconds=3)})
        f = create_should_print_date_fun(options)

        # Dates for post 0 and 4 has to be printed, because they do not have a
        # parent
        self.assertEquals(f(self._posts[0], section), True)
        self.assertEquals(f(self._posts[4], section), True)

        # Date for post 3 has to be printed, because its parent is much older
        # (much=4 seconds, but the 'timedelta' is 3)
        self.assertEquals(f(self._posts[3], section), True)

        # Dates for post 1 and 2 should not be printed, because they have
        # parents who are not much older than them
        self.assertEquals(f(self._posts[1], section), False)
        self.assertEquals(f(self._posts[2], section), False)

        # Flat section: all date has to be printed
        section[2]['flat'] = True
        self.assertEquals(f(self._posts[0], section), True)
        self.assertEquals(f(self._posts[1], section), True)
        self.assertEquals(f(self._posts[2], section), True)
        self.assertEquals(f(self._posts[3], section), True)
        self.assertEquals(f(self._posts[4], section), True)

    def test_create_date_fun(self):
        # sections
        section = ('', self._maildb.all(), {})
        sections = [section]
        heapmanip.Generator.sections_setdefaultoptions(sections)

        def my_should_fun(post, section):
            return post.heapid() in ['1', '3']
        # date options
        options = date_defopts({'maildb': self._maildb,
                                'should_print_date_fun': my_should_fun})
        f = create_date_fun(options)

        self.assertEquals(f(self._posts[0], section), None)
        self.assertNotEquals(f(self._posts[1], section), None)
        self.assertEquals(f(self._posts[2], section), None)
        self.assertNotEquals(f(self._posts[3], section), None)
        self.assertEquals(f(self._posts[4], section), None)

    def tearDown(self):
        self.tearDownDirs()

if __name__ == '__main__':
    heapmanip.set_log(False)
    unittest.main()