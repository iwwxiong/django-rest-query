#! /usr/bin/env python2
# -*-coding: utf-8 -*-
__author__ = 'dracarysX'

import copy
from django.views.generic import ListView
from django.views.generic.detail import DetailView, View
from django.http import JsonResponse
from django_rest_query import DjangoQueryBuilder, DjangoSerializer
from django_rest_query import RestQueryDetailViewMixin, RestQueryListViewMixin
#
from .models import Author, Book, School, Publisher


class HomeView(View):
    def get(self, *args, **kwargs):
        return JsonResponse({
            'authors': '/authors',
            'books': '/books',
            'schools': '/schools',
            'publishs': '/publishs',
        })


def author_detail(request, pk):
    get = copy.copy(request.GET)
    get.update({'id': pk})
    builder = DjangoQueryBuilder(Author, params=get)
    query = builder.build()
    try:
        obj = query.get()
    except Author.DoesNotExist:
        return JsonResponse({'code': 404, 'message': 'Not Found'}, status=404)
    serializer = DjangoSerializer(obj=obj, select_args=builder.parser.select_list)
    return JsonResponse(serializer.data())


def author_list(request):
    args = copy.copy(request.GET)
    builder = DjangoQueryBuilder(Author, params=args)
    paginate = True  # if you need not paging, set False
    query = builder.build(paginate=paginate)
    serializer = DjangoSerializer(
        object_list=query, 
        select_args=builder.parser.select_list
    )
    data = {
        'object_list': serializer.data()
    }
    if paginate:
        data.update({
            'page': builder.paginate['page'],
            'count': query.count(),
        })
    return JsonResponse(data)


class BookDetail(RestQueryDetailViewMixin, DetailView):
    model = Book


class BookList(RestQueryListViewMixin, ListView):
    model = Book


class SchoolDetail(RestQueryDetailViewMixin, DetailView):
    model = School


class SchoolList(RestQueryListViewMixin, ListView):
    model = School


class PublishDetail(RestQueryDetailViewMixin, DetailView):
    model = Publisher


class PublishList(RestQueryListViewMixin, ListView):
    model = Publisher
