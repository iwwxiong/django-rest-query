#! /usr/bin/env python
# -*-coding: utf-8 -*-
__author__ = 'dracarysX'

from django.db import models


class Publisher(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'Publisher'

    def __str__(self):
        return 'Publisher: {}'.format(self.name)


class School(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'School'

    def __str__(self):
        return 'School: {}'.format(self.name)


class Author(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    age = models.IntegerField()
    school = models.ForeignKey(School)

    class Meta:
        db_table = 'Author'

    def __str__(self):
        return 'Author: {}'.format(self.name)


class Book(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    author = models.ForeignKey(Author)
    publisher = models.ForeignKey(Publisher)

    class Meta:
        db_table = 'Book'

    def __str__(self):
        return 'Book: {}'.format(self.name)
