from rest_framework.pagination import CursorPagination
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response
from urllib.parse import urlparse, parse_qs


class PlainCursorPagination(CursorPagination):
    page_size = 10
    ordering = "-created_at"
    cursor_query_param = "cursor"


class PlainCursorPagination(PlainCursorPagination):
    def get_paginated_response(self, data):
        next_url = self.get_next_link()
        previous_url = self.get_previous_link()

        # Extract only the 'cursor' value from the full URL
        next_cursor = None
        if next_url:
            params = parse_qs(urlparse(next_url).query)
            next_cursor = params.get(self.cursor_query_param, [None])[0]

        prev_cursor = None
        if previous_url:
            params = parse_qs(urlparse(previous_url).query)
            prev_cursor = params.get(self.cursor_query_param, [None])[0]

        return Response({"next": next_cursor, "previous": prev_cursor, "results": data})
