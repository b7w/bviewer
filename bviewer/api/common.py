# -*- coding: utf-8 -*-
from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    page_size = 256
    max_page_size = 2048
