#! /usr/bin/env python3
# -*-coding: utf-8 -*-
__author__ = 'dracarysX'

from django.db import models


class School(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField()


class Author(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField()
    school = models.ForeignKey(School)


class Book(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField()
    author = models.ForeignKey(Author)
