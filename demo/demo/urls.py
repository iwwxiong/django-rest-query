"""demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
#
from .views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', HomeView.as_view()),
    # author
    url(r'^authors/(?P<pk>\d+)$', author_detail),
    url(r'^authors$', author_list),
    # book
    url(r'^books$', BookList.as_view()),
    url(r'^books/(?P<pk>\d+)$', BookDetail.as_view()),
    # school
    url(r'^schools$', SchoolList.as_view()),
    url(r'^schools/(?P<pk>\d+)$', SchoolDetail.as_view()),
    # publish
    url(r'^publishs$', PublishList.as_view()),
    url(r'^publishs/(?P<pk>\d+)$', PublishDetail.as_view()),
]
