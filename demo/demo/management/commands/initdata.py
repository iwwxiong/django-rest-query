#! /usr/bin/env python
# -*-coding: utf-8 -*-
__author__ = 'dracarysX'

"""
INIT DATA FOR THIS DEMO
"""

from django.core.management.base import BaseCommand
from demo.models import *


class Command(BaseCommand):
    
    def handle(self, *args, **options):
        s1 = School(name='BJ University')
        s2 = School(name='SH University')
        s1.save()
        s2.save()
        p1 = Publisher(name='RMDX')
        p2 = Publisher(name='HLJDX')
        p1.save()
        p2.save()
        a1 = Author(name='wwxiong', age=20, school=s2)
        a2 = Author(name='dracarysx', age=100, school=s1)
        a1.save()
        a2.save()
        b1 = Book(name='Python', author=a1, publisher=p2)
        b2 = Book(name='Javascript', author=a2, publisher=p1)
        b1.save()
        b2.save()
        print('Init data completed.')
