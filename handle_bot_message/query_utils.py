from consts import patient_type_key, person_types_keys


def extract_query_params(query: dict):
    page_size = 50
    starting_token = None
    person_type = patient_type_key

    page_size_key = 'page_size'
    if page_size_key in query and query[page_size_key].isdecimal():
        raw_page_size = int(query[page_size_key])
        if raw_page_size > 0 and page_size <= 5000:
            page_size = raw_page_size

    starting_token_key = 'starting_token'
    if starting_token_key in query and query[starting_token_key]:
        starting_token = query[starting_token_key]

    person_type_key = 'person_type'
    if person_type_key in query and query[person_type_key] and query[person_type_key] in person_types_keys:
        person_type = query[person_type_key]

    return page_size, starting_token, person_type