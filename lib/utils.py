def file_next_iterator(file_name):
    with open(file_name) as f:  
        for lineno, line in enumerate(f, start=1):
            yield lineno, line

