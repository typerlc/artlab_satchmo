# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.http import Http404
from django.test import TestCase
from models import *
import keyedcache
import logging

log = logging.getLogger('testimony.tests')
site = Site.objects.get_current()

class TestimonyCreateTest(TestCase):
    
    def testCreateSimple(self):
        ag = TestimonyGroup(key='tm.1', title='tm test 1', site = site)
        ag.save()
        
        self.assertEqual(str(ag), 'tm test 1')

class TestimonyTestGroups(TestCase):
    def setUp(self):
        ag = TestimonyGroup(key='tm.3', title='tm test 3', site=site)
        ag.save()

        self.grp = ag
        
        for i in range(1,11):
            s = Testimony(statement='tm.3.%i' % i, weight=1, status="ON", from_url="test.html")
            s.group = ag
            s.save()

    def testRandGroup(self):
        g = self.grp.random_testimonies(2)
        self.assertEqual(len(g),2)
        self.assertNotEqual(g[0].id,g[1].id)

        g2 = self.grp.random_testimonies(6)
        self.assertEqual(len(g2),6)
        d = {}
        for s in g2:
            d[s.id] = s
        
        self.assertEqual(len(d.keys()), 6)
        
class TestimonyTestWeighted(TestCase):
    def setUp(self):
        ag = TestimonyGroup(key='tm.4', title='tm test 4', site=site)
        ag.save()
        self.grp = ag
        
        s = Testimony(statement='tm.4.0', weight=1000, status="ON", from_url="test.html")
        s.group = ag
        s.save()
        self.heavy = s

        for i in range(2,11):
            s2 = Testimony(group = ag, statement='tm.4.%i' % i, weight=1, status="ON", from_url="test.html")
            s2.save()

    def testRandGroup(self):
        for i in range(0,50):
            g = self.grp.random_ids(2)
            self.assertNotEqual(g[0], g[1])
            self.assert_(self.heavy.id in g)
        
        
