"""Helpers module."""


def clear_search_query(query: str):
    for c in '&|!(){}[]^"~*?:':
        query = query.replace(c, '')
    return query
