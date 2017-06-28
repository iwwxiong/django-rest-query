# django-rest-query

A rest query request args parser for django orm. like no-sql select style.(/?select=id,name,author{*}&id=gte.20&order=id.desc).
depend on [rest-query](https://github.com/dracarysX/rest-query).

## Installing

    > pip install django-rest-query

## Test

    > python setup.py test

## Usage

Django orm must use project shell. so wo start demo project

    django-admin startproject demo

Add Model

```python
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
```

Usage

```python
python manage.py shell
> from django_rest_query import *
> from demo.models import Book, Author, School
> args = {
        'select': 'id,name,author{id,name,school{*}}',
        'id': 'gte.20',
        'author.id': 'in.10,20,30,40,50',
        'order': 'id.desc',
        'page': 1,
        'limit': 5
    }
> builder = DjangoQueryBuilder(Book, args)
> builder.select
['author__school__*', 'author__id', 'author__name', 'id', 'name']
> build.where
{'author__id__in': [10, 20, 30, 40, 50], 'id__gte': '20'}
> builder.order
['-id']
> builder.paginate
(1, 5)
{'start': 0, 'end': 5, 'limit': 5, 'page': 1}
> builder.build()
<QuerySet [Book: Python], [Book: Javascript]>
```

## Demo

Start Server

```bash
cd cdmo
virtualenv --no-site-packages venv
source venv/bin/activate
pip install django djang-rest-query
python manage.py makemigrations demo
python manage.py migrate
python manage.py runserver
```

API Query

curl http://127.0.0.1:8000/books?select=id,name,author{id,school{*}}&id=lte.10&order=id.desc

```json
{
    "count": 2,
    "object_list": [
        {
            "id": 2,
            "name": "Javascript",
            "author": {
                "school": {
                    "id": 1,
                    "name": "BJ University"
                },
                "id": 2
            }
        },
        {
            "id": 1,
            "name": "Python",
            "author": {
                "school": {
                    "id": 2,
                    "name": "SH University"
                },
                "id": 1
            }
        }
    ],
    "is_paginated": false,
    "page": 1
}
```

curl http://127.0.0.1:8000/books/1?select=id,name,author{name}

```json
{
    "id": 1,
    "name": "Python",
    "author": {
        "name": "wwxiong"
    }
}
```

## License

MIT

## Contacts

Email: huiquanxiong@gmail.com
