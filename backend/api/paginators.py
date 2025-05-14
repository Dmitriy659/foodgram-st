from rest_framework.pagination import PageNumberPagination


class ApiPagination(PageNumberPagination):
    """
    Пагинация
    """
    page_size = 3  # TODO изменить
    page_size_query_param = "limit"
    page_query_param = "page"

