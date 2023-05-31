def count_variables(cond, is_runtime=0):
    variable_count = len([x for x in cond if x[0] == '?'])
    return 4 - variable_count if is_runtime else 3 - variable_count


def is_condition_matching(condition_database, condition_query, is_query_brand=False):
    if not is_query_brand:
        if len(condition_database) != len(condition_query):
            return False
        for index in range(len(condition_database)):
            if condition_query[index][0] != '?':
                if condition_query[index] != condition_database[index]:
                    return False
        return True
    else:
        if len(condition_database) != len(condition_query) or condition_database[0] != 'ATIME':
            return False
        if condition_query[0] == condition_database[0]:
            if condition_query[3] == 'vietjet air':
                if condition_database[1][:2] != 'VJ':
                    return False
            elif condition_query[3] == 'vietnam airlines':
                if condition_database[1][:2] != 'VN':
                    return False
        return True


def join_list_elements(lst):
    if not lst:
        return ''
    return ' '.join(lst)


def join_variable_questions(lst):
    if not lst:
        return 
    return ', '.join(lst)


def convert_list_to_parenthesized_string(lst, flag=0):
    if all(x[0] == '?' for x in lst[1:]) and all(x[2] == '1' for x in lst[1:]) and flag == 0:
        return ''
    if flag == 2:
        if not all(x[0] != '?' for x in lst[2:-1]):
            return ''
    s = ' '.join(lst)
    return f'({s.strip()})'
