from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    page_size_query_param = "limit"
    max_page_size = 100


class RecipeLimitPageNumberPagination(PageNumberPagination):
    page_size_query_param = "recipe_limit"
    max_page_size = 100
