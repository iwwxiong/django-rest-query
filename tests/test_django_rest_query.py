#! /usr/bin/env python3
# -*-coding: utf-8 -*-
__author__ = 'dracarysX'

"""
Test case for django, require Django1.6x package.
"""

import os
import unittest
import django
from django.db.models.query import QuerySet
from django_rest_query import *
from django.core.wsgi import get_wsgi_application
from django.db import models

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "book.settings")
application = get_wsgi_application()


class DjangoOperatorTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.operator_v1 = DjangoOperator('author.id', 100)
        cls.operator_v2 = DjangoOperator('author.name', 'wwx,wwxiong')
        cls.operator_v3 = DjangoOperator('author.id', '10,20')
    
    def test_eq(self):
        self.assertDictEqual(self.operator_v1.eq(), {'author__id': 100})

    def test_neq(self):
        self.assertDictEqual(self.operator_v1.neq(), {'author__id__neq': 100})

    def test_gt(self):
        self.assertDictEqual(self.operator_v1.gt(), {'author__id__gt': 100})

    def test_gte(self):
        self.assertDictEqual(self.operator_v1.gte(), {'author__id__gte': 100})

    def test_lt(self):
        self.assertDictEqual(self.operator_v1.lt(), {'author__id__lt': 100})

    def test_lte(self):
        self.assertDictEqual(self.operator_v1.lte(), {'author__id__lte': 100})

    def test_like(self):
        self.assertDictEqual(self.operator_v1.like(), {'author__id__contains': 100})

    def test_ilkie(self):
        self.assertDictEqual(self.operator_v1.ilike(), {'author__id__icontains': 100})

    def test_iin(self):
        self.assertDictEqual(self.operator_v2.iin(), {'author__name__in': ['wwx', 'wwxiong']})

    def test_between(self):
        self.assertDictEqual(self.operator_v3.between(), {'author__id__range': [10, 20]})


class DjangoParamsParserTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        from book.models import Book
        args = {
            'select': 'id,name,author{id,name,school{id,name}}',
            'id': 'gt.10', 
            'age': 'lte.25',
            'name': 'in.python, javascript',
            'order': 'id.desc',
            'page': 2,
            'limit': 5
        }
        cls.parser = DjangoParamsParser(params_args=args, model=Book)
    
    def test_parse_select(self):
        self.assertIn('id', self.parser.parse_select())
        self.assertIn('name', self.parser.parse_select())
        self.assertIn('author__id', self.parser.parse_select())
        self.assertIn('author__name', self.parser.parse_select())
        self.assertIn('author__school__id', self.parser.parse_select())
        self.assertIn('author__school__name', self.parser.parse_select())

    def test_parse_where(self):
        self.assertEqual(self.parser.parse_where()['id__gt'], '10')
        self.assertNotIn('age__lte', self.parser.parse_where())
        self.assertEqual(self.parser.parse_where()['name__in'], ['python', 'javascript'])

    def test_parse_order(self):
        self.assertIn('-id', self.parser.parse_order())

    def test_parse_paginate(self):
        self.assertDictEqual({'start': 5, 'end': 10, 'limit': 5, 'page': 2}, self.parser.parse_paginate())


class DjangoQueryBuilderTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        from book.models import Book, Author, School

        school = School(id=1, name='Tsinghua University')
        author1 = Author(id=1, name='wwxiong', school=school)
        author2 = Author(id=2, name='wwx', school=school)
        book1 = Book(id=1, name='Python', author=author1)
        book2 = Book(id=1, name='Javascript', author=author2)
        cls.school, cls.author1, cls.author2, cls.book1, cls.book2 = (school, author1, author2, book1, book2)
        cls.builder = DjangoQueryBuilder(
            model=Book,
            params={
                'select': 'id,name,author{id,name,school{id,name}}',
                'id': 'lte.2', 
                'name': 'in.Python, Javascript',
                'order': 'id.desc',
                'page': 1,
                'limit': 1
            }
        )
    
    def test_build(self):
        from book.models import Book

        queryset = Book.objects.values(
            'id', 'name', 'author__id', 'author__name', 'author__school__id', 'author__school__name'
        ).filter(id__lte=2, name__in=['Python', 'Javascript']).exclude().order_by('-id')[0:1]
        # print(queryset.query.select)
        # print(queryset.query.where)
        # print(queryset.query.values_select)
        # print(queryset.query.sql_with_params())
        self.assertIsInstance(self.builder.build(), QuerySet)


if __name__ == '__main__':
    unittest.main()
