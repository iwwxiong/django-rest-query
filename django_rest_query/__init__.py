#! /usr/bin/env python
# -*-coding: utf-8 -*-

__author__ = 'dracarysX'

import copy
from django.core.exceptions import FieldDoesNotExist
from django.http import JsonResponse
from django.db.models import ForeignKey
#
from rest_query.operator import Operator
from rest_query.query import QueryBuilder
from rest_query.parser import BaseParamsParser, DESC
from rest_query.models import ModelExtra
from rest_query.serializer import BaseSerializer


class DjangoModelExtraMixin(ModelExtra):
    """
    django mode
    """
    all_field = '*'

    def field_by_model(self, model, field_name):
        try:
            field = model._meta.get_field(field_name)
        except FieldDoesNotExist:
            field = None
        return field

    def is_field_exist(self, model, field_name):
        if field_name == self.all_field:
            return True
        return self.field_by_model(model, field_name) is not None

    def foreign_model(self, field):
        return field.related_model


class DjangoOperator(Operator):
    """
    operator for django
    """
    def __init__(self, field_name, value, **kwargs):
        super(DjangoOperator, self).__init__(field_name, value)
        if len(self.field_name.split('.')) > 1:
            self.field_name = self.field_name.replace('.', '__')

    def eq(self):
        return {self.field_name: self.value}

    def neq(self):
        """
        django neq must use exclude.
        """
        return {'{}__neq'.format(self.field_name): self.value}

    def gt(self):
        return {'{}__gt'.format(self.field_name): self.value}

    def gte(self):
        return {'{}__gte'.format(self.field_name): self.value}

    def lt(self):
        return {'{}__lt'.format(self.field_name): self.value}

    def lte(self):
        return {'{}__lte'.format(self.field_name): self.value}

    def like(self):
        return {'{}__contains'.format(self.field_name): self.value}

    def ilike(self):
        return {'{}__icontains'.format(self.field_name): self.value}

    def iin(self):
        return {'{}__in'.format(self.field_name): self._split_value()}

    def between(self):
        return {'{}__range'.format(self.field_name): self._split_value()}


class DjangoParamsParser(DjangoModelExtraMixin, BaseParamsParser):
    """
    inherit BaseParamsParser, override function parse_select, parse_where, parse_order, parse_paginate
    """
    operator_engine = DjangoOperator

    def __init__(self, params_args, model=None, **kwargs):
        super(DjangoParamsParser, self).__init__(params_args, **kwargs)
        self.model = model
        self.foreign_key = ForeignKey

    def parse_select(self):
        selects = super(DjangoParamsParser, self).parse_select()
        self.select_list = [select.replace('.', '__') for select in filter(self.check_field_exist, selects)]
        return self.select_list

    def split_where(self):
        _wheres = []
        for field, values in self.where_args.items():
            try:
                _value = values.split('.')
                operator, value = _value[0], '.'.join(_value[1:])
            except AttributeError:
                operator, value = '=', values
            if self.check_field_exist(field):
                if operator not in self.operator_list:
                    _wheres.append(self.operator_engine(field, values).eq())
                else:
                    _wheres.append(
                        getattr(self.operator_engine(field, value), operator)()
                    )
        return _wheres

    def parse_where(self):
        wheres = super(DjangoParamsParser, self).parse_where()
        _where = {}
        for where in wheres:
            _where.update(where)
        return _where

    def parse_exclude(self):
        
        def _is_exclude(w):
            for i in w.keys():
                if i.endswith('__neq'):
                    return True
            return False

        wheres = super(DjangoParamsParser, self).parse_where()
        _exclude = {}
        for where in wheres:
            if _is_exclude(where):
                _exclude.update(where)
        return _exclude

    def parse_order(self):
        orders = super(DjangoParamsParser, self).parse_order()
        _order = []
        for order in orders:
            for key, value in order.items():
                if self.check_field_exist(key):
                    if value == DESC:
                        key = '-{}'.format(key)
                    _order.append(key)
        return _order


class DjangoQueryBuilder(QueryBuilder):
    """
    queryset builder for django orm
    """
    parser_engine = DjangoParamsParser

    def __init__(self, model, params, **kwargs):
        super(DjangoQueryBuilder, self).__init__(model, params, **kwargs)
        self.exclude = self.parser.parse_exclude()
    
    def get_select_related(self):
        select_related = []
        for select in self.select:
            if select.find('__') != -1:
                select_related.append('__'.join(select.split('__')[:-1]))
        return set(select_related)

    def build(self, paginate=False):
        query = self.model.objects.filter(**self.where)
        if self.exclude:
            query = query.exclude(**self.exclude)
        if self.order:
            query = query.order_by(*self.order)
        if paginate and self.paginate:
            query = query[self.paginate['start']:self.paginate['end']]
        select_related = self.get_select_related()
        if select_related:
            query = query.select_related(*select_related)
        return query


class DjangoSerializer(BaseSerializer):
    """
    serializer for django object instance.
    >>> serializer = DjangoSerializer(obj=book, select_args=['id', 'name', 'author.id', 'author.name'])
    >>> serializer.data()
    {
        'id': xxx,
        'name': 'xxx',
        'author': {
            'id': xxx,
            'name': 'xxx'
        }
    }
    >>> serializer = DjangoSerializer(object_list=book_list, select_args=['id', 'name', 'author.id', 'author.name'])
    >>> serializer.data()
    [
        {
            'id': xxx,
            'name': 'xxx',
            'author': {
                'id': xxx,
                'name': 'xxx'
            }
        },
        {
            'id': xxx,
            'name': 'xxx',
            'author': {
                'id': xxx,
                'name': 'xxx'
            }
        }
    ]
    """
    def _obj_update(self, o1, o2):
        """
        o1 update o2, if key in o1 not override
        """
        for key, value in o2.items():
            if key not in o1 or (key in o1 and isinstance(o1[key], int)):
                o1[key] = value
        return o1

    def obj_serializer(self, obj):
        if isinstance(obj, dict):
            return obj
        return {k.name: getattr(obj, k.name if not isinstance(k, ForeignKey) else '%s_id' % k.name)
                for k in obj.__class__._meta.fields}

    def _getattr(self, obj, field):
        value = getattr(obj, field)
        if hasattr(value, 'DoesNotExist'):
            return getattr(obj, '{}_id'.format(field))
        return value

    def serializer(self, obj):
        if not self.select_args:
            return self.obj_serializer(obj)
        data = {}

        def _serializer(_data, select, obj):
            args = select.split('__')
            if len(args) == 1:
                if select == '*':
                    _data = self._obj_update(_data, self.obj_serializer(obj))
                else:
                    if select not in _data:
                        _data[select] = self._getattr(obj, select)
                    else:
                        if not isinstance(_data[select], dict):
                            _data[select] = self._getattr(obj, select)
            else:
                prefix = args[0]
                if prefix not in _data:
                    _data[prefix] = {}
                _serializer(_data[prefix], '__'.join(args[1:]), getattr(obj, prefix))

        for i in self.select_args:
            _serializer(data, i, obj)

        return data


class RestQueryMixin(object):
    
    serializer_class = DjangoSerializer

    def get_object(self, queryset=None):
        args = copy.copy(self.request.GET)
        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg)
        if pk is not None:
            pk_field = self.model._meta.pk
            args.update({pk_field.name: pk})
        if slug is not None:
            args.update({self.get_slug_field(): slug})

        self.builder = DjangoQueryBuilder(self.model, args)
        try:
            obj = self.builder.build().get()
        except self.model.DoesNotExist:
            raise self.mode.DoesNotExist
        return obj


class RestQueryListMixin(object):

    context_object_name = 'object_list'
    paginate_by = 10

    def get_queryset(self):
        """
        overvide
        """
        args = copy.copy(self.request.GET)
        self.builder = DjangoQueryBuilder(self.model, args)
        return self.builder.build(paginate=False)

    def get_paginate_by(self, queryset):
        return self.builder.paginate['limit']

    def get_context_data(self, **kwargs):
        data = super(RestQueryListMixin, self).get_context_data(**kwargs)
        serializer = self.serializer_class(
            object_list=data['object_list'],
            select_args=self.builder.parser.select_list
        )
        data.pop('object_list')
        data.pop('view')
        data[self.context_object_name] = serializer.data()
        data['count'] = data['paginator'].count
        # data['num_pages'] = data['paginator'].num_pages
        data.update({
            'page': self.builder.paginate['page']
        })
        data.pop('paginator')
        data.pop('page_obj')
        return data


class RestQueryDetailViewMixin(RestQueryMixin):

    def get(self, *args, **kwargs):
        try:
            obj = self.get_object()
        except self.model.DoesNotExist:
            return JsonResponse({'code': 404, 'message': 'Not Found'}, status=404)
        serializer = self.serializer_class(obj=obj, select_args=self.builder.parser.select_list)
        return JsonResponse(serializer.data())


class RestQueryListViewMixin(RestQueryMixin, RestQueryListMixin):

    def get(self, *args, **kwargs):
        self.object_list = self.get_queryset()
        return JsonResponse(self.get_context_data())
