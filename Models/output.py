import re
from Models.utils import join_list_elements, join_variable_questions, convert_list_to_parenthesized_string


def print_relation(relations):
    output = ''

    for r in relations:
        if r[1] == "ROOT":
            output += f'{r[0]}: {r[2][2]}\n'
        else:
            output += f'{r[0]}: {r[1][2]} -> {r[2][2]}\n'

    # Return the resulting string representation of the relations
    return output


def print_grammatical_relations(grammatical_relations):
    if not grammatical_relations:
        return

    output = ""
    for i in grammatical_relations:
        output += f'({i[0]} {i[1]} "{i[2][2]}")\n'
    return output


def print_logical_form(args):
    if not args:
        return ''

    vars_question, flight, source, dest, arrive, depart, run_time, _brand_name = args
    return f'WH {join_variable_questions(vars_question)}:' \
           f' (&{join_list_elements(flight)}' \
           f' {join_list_elements(source)}' \
           f' {join_list_elements(dest)} ' \
           f' {join_list_elements(arrive)}' \
           f' {join_list_elements(depart)}' \
           f' {join_list_elements(run_time)})\n'


def print_procedural_semantic(procedural_semantic_args):
    if not procedural_semantic_args:
        return ''

    vars_question, flight, arrival_time, departure_time, runtime, brand_name = procedural_semantic_args
    output = f'(PRINT-ALL {join_variable_questions(vars_question)} ' \
             f'{convert_list_to_parenthesized_string(flight, 1)} ' \
             f'{convert_list_to_parenthesized_string(brand_name)} ' \
             f'{convert_list_to_parenthesized_string(departure_time)}' \
             f' {convert_list_to_parenthesized_string(arrival_time)}' \
             f' {convert_list_to_parenthesized_string(runtime, 2)})\n'
    output = f"{re.sub(' +', ' ', output).strip()}\n"
    return output


def print_output(answers_dict):
    if not answers_dict:
        return ''

    if '?y1' in answers_dict and answers_dict['?y1'] == 'Yes':
        return 'Answer: Yes'
    elif '?y2' in answers_dict and answers_dict['?y2'] == 'No':
        return 'Answer: No'

    keys1 = ['?f1', '?t1', '?t2', '?t3', '?c1', '?c2']
    keys2 = ['Flights', 'Depart Time', 'Arrive Time', 'Run Time', 'Source', 'Destination']

    output = ''
    for key, value in answers_dict.items():
        if key in keys1:
            index = keys1.index(key)
            output += f'{keys2[index]}: {join_variable_questions(value)}\n'

    return output
