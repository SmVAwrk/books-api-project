from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import generics

from books.models import Books, Authors, Categories, Libraries
from books.serializers import BooksSerializer, AuthorsSerializer, CategoriesSerializer, LibrariesSerializer


class BooksAPIView(generics.ListAPIView):
    queryset = Books.objects.all().order_by('-created_at')
    serializer_class = BooksSerializer


class AuthorsAPIView(generics.ListAPIView):
    queryset = Authors.objects.all().order_by('last_name')
    serializer_class = AuthorsSerializer


class CategoriesAPIView(generics.ListAPIView):
    queryset = Categories.objects.all().order_by('title')
    serializer_class = CategoriesSerializer


class LibrariesAPIView(generics.ListAPIView):
    queryset = Libraries.objects.all().order_by('title')
    serializer_class = LibrariesSerializer
