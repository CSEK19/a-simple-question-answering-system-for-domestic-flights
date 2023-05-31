import re
from unidecode import unidecode
from Input.dictionary import tag_dictionary
from Models.utils import count_variables, is_condition_matching


def normalize_city_word(string):
    string = string.replace('TP.', 'thành phố ').replace('Tp.', 'thành phố ').strip().lower()
    return string


def left_arc(relations, r, input_buffer, stack):
    relations.append((r, input_buffer[0], stack[-1]))
    stack.pop(-1)


def right_arc(relations, r, input_buffer, stack):
    relations.append((r, stack[-1], input_buffer[0]))
    stack.append(input_buffer.pop(0))


def shift(stack, input_buffer):
    stack.append(input_buffer.pop(0))


def reduce(stack):
    stack.pop(-1)


def extract_tagged_words(query):
    if not query:
        return 
    
    tag_word_list = []
    normalized_query = unidecode(query)

    for tag_entry in tag_dictionary:
        if 'tag' in tag_entry and 'regex' in tag_entry:
            tag = tag_entry['tag']
            regex = tag_entry['regex']
            matches = re.finditer(regex, normalized_query)

            for match in matches:
                start, end = match.start(), match.end()
                group, substring = match.group(), query[start:end]
                tag_word_list.append((start, end, tag, group, substring))

    tag_word_list.sort()

    remove_list = []
    for i in tag_word_list:
        for j in tag_word_list:
            if i is not j and i[1] > j[0] and i[0] < j[1]:
                if i[1] - i[0] < j[1] - j[0]:
                    remove_list.append(i)
                else:
                    remove_list.append(j)

    tag_word_list = [elem for elem in tag_word_list if elem not in remove_list]
    return_list = [(elem[2], elem[3], elem[4]) for elem in tag_word_list]

    flag_flight_name = False
    flag_yes_wh = False

    for tag in return_list:
        if tag[0] == 'FLIGHT-NAME':
            flag_flight_name = True
        elif tag[0] == 'YES-WH':
            flag_yes_wh = True

    flag_yes_question = False
    if flag_flight_name and flag_yes_wh:
        flag_yes_question = True

    return return_list, flag_yes_question


def build_dependency_relations(tag_word_list):
    if not tag_word_list:
        return

    relations = []
    stack = ['ROOT']
    input_buffer = tag_word_list.copy()
    input_buffer = [x for x in input_buffer if x[0] not in ['YES-WH', 'NO-WH']]

    while len(input_buffer) != 0:
        if stack[-1] == 'ROOT':
            if input_buffer[0][0] in ['ARRIVE-VERB-PREP', 'FLIGHT-VERB', 'FLIGHT-ARRIVE', 'FLIGHT-DEPART', 'LAST-PREP']:
                if 'root' not in [x[0] for x in relations]:
                    right_arc(relations, 'root', input_buffer, stack)
                    continue

        if stack[-1][0] in ['ARRIVE-VERB-PREP']:
            if input_buffer[0][0] in ['CITY-NAME', 'CITY-NOUN']:
                if 'root' in [x[0] for x in relations]:
                    root_relation = next(x for x in relations if x[0] == 'root')
                    if root_relation[2][1] != 'den':
                        if input_buffer[0][0] == 'CITY-NOUN' and input_buffer[1][0] == 'CITY-NAME':
                            shift(stack, input_buffer)
                            continue
                        left_arc(relations, 'case', input_buffer, stack)
                        continue
                    if input_buffer[0][0] == 'CITY-NOUN' and input_buffer[1][0] == 'CITY-NAME':
                        shift(stack, input_buffer)
                        continue
                    right_arc(relations, 'obl', input_buffer, stack)
                    continue
                elif stack[1][0] == 'TIME-NOUN':
                    left_arc(relations, 'case', input_buffer, stack)
                    continue
            if input_buffer[0][0] in ['FLIGHT-TIME-DEPT-TO-ARRI']:
                right_arc(relations, 'obl', input_buffer, stack)
                continue
            if input_buffer[0][0] in ['PUNC']:
                right_arc(relations, 'punc', input_buffer, stack)
                continue

        if stack[-1][0] in ['FLIGHT-NOUN', 'FLIGHT-NAME', 'FLIGHT-ID-NOUN']:
            if input_buffer[0][0] == 'QDET':
                right_arc(relations, 'qdet', input_buffer, stack)
                continue
            if input_buffer[0][0] in ['ARRIVE-VERB-PREP', 'FLIGHT-VERB', 'FLIGHT-ARRIVE', 'FLIGHT-DEPART']:
                if stack[1][0] == 'TIME-NOUN':
                    right_arc(relations, 'acl', input_buffer, stack)
                    continue
                left_arc(relations, 'nsubj', input_buffer, stack)
                continue
            if stack[-1][1] == 'ma hieu' and input_buffer[0][1] == 'may bay':
                left_arc(relations, 'nmod', input_buffer, stack)
                continue
            if input_buffer[0][0] == 'FLIGHT-NAME':
                left_arc(relations, 'nmod', input_buffer, stack)
                continue
            if input_buffer[0][0] == 'BRAND-NAME':
                right_arc(relations, 'aposs', input_buffer, stack)
                continue
            if stack[1][0] == 'TIME-NOUN':
                reduce(stack)
                continue

        if stack[-1][0] in ['FLIGHT-VERB', 'FLIGHT-ARRIVE', 'FLIGHT-DEPART']:
            if input_buffer[0][0] in ['CITY-NAME', 'HOUR-NOUN']:
                right_arc(relations, 'obl', input_buffer, stack)
                continue
            if input_buffer[0][0] == 'CITY-NOUN' and input_buffer[1][0] != 'CITY-NAME':
                right_arc(relations, 'obl', input_buffer, stack)
                continue
            if input_buffer[0][0] in ['PUNC']:
                right_arc(relations, 'punc', input_buffer, stack)
                continue
            if input_buffer[0][0] in ['LAST-PREP']:
                if stack[1][0] == 'TIME-NOUN':
                    reduce(stack)
                    continue
                right_arc(relations, 'advmod', input_buffer, stack)
                continue

        if stack[-1][0] == 'QDET':
            if stack[-1][1] == 'hay cho biet':
                if input_buffer[0][0] in ['FLIGHT-NOUN', 'FLIGHT-ID-NOUN']:
                    left_arc(relations, 'qdet', input_buffer, stack)
                    continue
            if input_buffer[0][0] in ['HOUR-NOUN']:
                left_arc(relations, 'qdet', input_buffer, stack)
                continue
            reduce(stack)
            continue

        if stack[-1][0] in ['CITY-NOUN']:
            if input_buffer[0][0] in ['CITY-NAME']:
                left_arc(relations, 'nmod', input_buffer, stack)
                continue
            if input_buffer[0][0] in ['QDET']:
                right_arc(relations, 'qdet', input_buffer, stack)
                continue

        if stack[-1][0] in ['CITY-NAME']:
            reduce(stack)
            continue

        if stack[-1][0] in ['AT-PREP']:
            if input_buffer[0][0] in ['FLIGHT-TIME-DEPT-TO-ARRI', 'HOUR-NOUN']:
                left_arc(relations, 'case', input_buffer, stack)
                continue

        if stack[-1][0] in ['FROM-PREP', 'TO-P', 'IN-PREP']:
            if input_buffer[0][0] in ['CITY-NAME']:
                left_arc(relations, 'case', input_buffer, stack)
                continue

        if stack[-1][0] in ['LAST-PREP']:
            if input_buffer[0][0] in ['HOUR-NOUN']:
                right_arc(relations, 'dobj', input_buffer, stack)
                continue
            if input_buffer[0][0] in ['PUNC']:
                root_relation = next(x for x in relations if x[0] == 'root')
                if root_relation[2][1] != 'den':
                    right_arc(relations, 'punc', input_buffer, stack)
                    continue

        if stack[-1][0] in ['PLURAL-DET']:
            if input_buffer[0][0] in ['FLIGHT-NOUN', 'CITY-NOUN', 'FLIGHT-ID-NOUN']:
                left_arc(relations, 'det', input_buffer, stack)
                continue
        
        if stack[-1][0] in ['FLIGHT-TIME-NUMBER']:
            if input_buffer[0][0] in ['HOUR-NOUN']:
                left_arc(relations, 'nummod', input_buffer, stack)
                continue

        if stack[-1][0] in ['TIME-NOUN']:
            if input_buffer[0][0] in ['FLIGHT-NAME']:
                right_arc(relations, 'nmod', input_buffer, stack)
                continue
            if input_buffer[0][0] in ['LAST-PREP']:
                left_arc(relations, 'nsubj', input_buffer, stack)
                continue

        if stack[-1][0] in ['POSS-PREP']:
            if input_buffer[0][0] == 'BRAND-NAME':
                left_arc(relations, 'case', input_buffer, stack)
                continue

        if input_buffer[0][0] == 'PUNC':
            if stack[-1][0] not in ['ARRIVE-VERB-PREP', 'FLIGHT-VERB']:
                reduce(stack)
                continue

        if stack[-1][0] in ['BRAND-NOUN']:
            if input_buffer[0][0] == 'BRAND-NAME':
                left_arc(relations, 'nmod', input_buffer, stack)
                continue

        if stack[-1][0] in ['BRAND-NAME']:
            reduce(stack)
            continue

        shift(stack, input_buffer)
    return relations


def add_grammatical_relations(grammatical_relations, var, grammar, word):
    grammatical_relations.append((var, grammar, word))


def build_grammatical_relations(relations):
    if not relations:
        return
    
    grammatical_relations = []

    root = [x for x in relations if x[0] == 'root'][0]
    add_grammatical_relations(grammatical_relations, 's1', 'PRED', root[2])
    nsubj = [x for x in relations if x[0] == 'nsubj'][0]
    add_grammatical_relations(grammatical_relations, 's1', 'LSUBJ', nsubj[2])
    dobj = [x for x in relations if x[0] == 'dobj']
    
    if len(dobj) != 0:
        add_grammatical_relations(grammatical_relations, 's1', 'LOBJ', dobj[0][2])

    acls = [x for x in relations if x[0] == 'acl']
    for acl in acls:
        add_grammatical_relations(grammatical_relations, 's2', 'LSUBJ', acl[1])
        add_grammatical_relations(grammatical_relations, 's2', 'PRED', acl[2])
        stack_add = []
        stack_delete = []
        for ele in grammatical_relations:
            if ele[1] not in ['PRED', 'LSUBJ', 'LOBJ']:
                stack_add.append(('s2', ele[1], ele[2]))
                stack_delete.append(ele)
        [grammatical_relations.pop(grammatical_relations.index(ele)) for ele in stack_delete]
        grammatical_relations += stack_add

    advmods = [x for x in relations if x[0] == 'advmod']
    for advmod in advmods:
        if advmod[2][1] == 'mat':
            unit = None
            for relation in relations:
                if relation[0] == 'dobj' and relation[1][1] == 'mat':
                    unit = relation[2][1]
                    break
            num = None
            for relation in relations:
                if relation[0] == 'nummod' and relation[1][1] == unit:
                    num = relation[2][1]
                    break
            unit = 'HR' if unit == 'gio' else unit
            add_grammatical_relations(grammatical_relations, 's1', 'TAKE', f'{num}:00{unit}')

    cases = [x for x in relations if x[0] == 'case']
    for case in cases:
        if case[1][0] in ['CITY-NAME', 'CITY-NOUN']:
            if case[2][0] in ['FROM-PREP']:
                add_grammatical_relations(grammatical_relations, 's1', 'FROM', case[1])
            if case[2][0] in ['ARRIVE-VERB-PREP']:
                add_grammatical_relations(grammatical_relations, 's1', 'TO', case[1])
        if case[1][0] in ['HOUR-NOUN']:
            if case[2][0] in ['AT-PREP']:
                add_grammatical_relations(grammatical_relations, 's1', 'AT-TIME', case[1])

    obls = [x for x in relations if x[0] == 'obl']
    for obl in obls:
        if obl[1][0] in ['ARRIVE-VERB-PREP', 'FLIGHT-ARRIVE']:
            if obl[2][0] in ['CITY-NAME']:
                add_grammatical_relations(grammatical_relations, 's1', 'TO', obl[2])
            elif obl[2][0] in ['FLIGHT-TIME-DEPT-TO-ARRI']:
                add_grammatical_relations(grammatical_relations, 's1', 'AT-TIME', obl[2])

    return grammatical_relations


def construct_logical_form(relations, grammatical_relations):
    if not grammatical_relations:
        return
    
    source = []
    dest = []
    run_time = []
    arrive = []
    depart = []
    brand_name = []

    lsubj = None
    pred = None
    name_time = None

    for relation in relations:
        if relation[0] == 'nmod' and relation[1][0] == 'BRAND-NAME':
            brand_name = [relation[1][0], 'f1', relation[1][2]]

    for relation in grammatical_relations:
        if relation[1] == 'LSUBJ':
            lsubj = relation
            break

    if lsubj is not None:
        try:
            lsubj = [x for x in grammatical_relations if x[1] == 'LSUBJ'][1]
        except IndexError:
            pass

    if lsubj is not None and lsubj[2][0] == 'FLIGHT-NAME':
        flight = ['FLIGHT', lsubj[2][1]]
    else:
        flight = ['FLIGHT', 'f1']

    # AT-TIME
    for relation in grammatical_relations:
        if relation[1] == 'PRED':
            pred = relation
            break
    if pred is not None and pred[2][0] == 'LAST-PREP':
        run_time = ['RUN-TIME', 'r1', 't3']
    for relation in grammatical_relations:
        if relation[1] == 'AT-TIME':
            name_time = relation[2][2]
            break
    if name_time is not None and pred is not None:
        if pred[2][0] == 'ARRIVE-VERB-PREP':
            arrive = ['ARRIVE', 'a1', f'(NAME t2 "{name_time}")']
        elif pred[2][0] == 'FLIGHT-DEPART':
            depart = ['DEPART', 'd1', f'(NAME t1 "{name_time}")']

    # FROM
    if 'FROM' in [x[1] for x in grammatical_relations]:
        name_source = [x[2][2] for x in grammatical_relations if x[1] == 'FROM'][0]
        source = ['SOURCE', flight[1], f'(NAME c1 "{name_source}")']

    # TAKE
    if 'TAKE' in [x[1] for x in grammatical_relations]:
        name_hour = [x[2] for x in grammatical_relations if x[1] == 'TAKE'][0]
        run_time = ['RUN-TIME', 'r1', f'(NAME t3 "{name_hour}")']

    # TO
    if 'TO' in [x[1] for x in grammatical_relations]:
        name_to = [x[2][2] for x in grammatical_relations if x[1] == 'TO'][0]
        dest = ['DEST', flight[1], f'(NAME c2 "{name_to}")']

    qdets = []
    vars_question = []
    try:
        qdets = [x for x in relations if x[0] == 'qdet']

        for qdet in qdets:
            if qdet[1][0] in ['FLIGHT-NOUN', 'FLIGHT-ID-NOUN']:
                vars_question.append(flight[1])
            elif qdet[1][0] == 'HOUR-NOUN':
                temp_list = [depart, arrive, run_time]
                first_non_empty = None

                for item in temp_list:
                    if item:
                        first_non_empty = item
                        break

                if first_non_empty is not None:
                    index = 1 + temp_list.index(first_non_empty)
                    vars_question.append(f't{index}')
            elif qdet[1][0] == 'CITY-NOUN':
                from_cities = [x for x in grammatical_relations if x[1] == 'FROM']
                to_cities = [x for x in grammatical_relations if x[1] == 'TO']

                for ele in from_cities + to_cities:
                    if ele[2][0] != 'CITY-NAME':
                        if ele[1] == 'TO':
                            vars_question.append('c2')
                        elif ele[1] == 'FROM':
                            vars_question.append('c1')
    except IndexError:
        vars_question.append(flight[1])

    if len(qdets) == 0:  # WH question
        flight[1] = 'f1'
        if source:
            source[1] = 'f1'
        if dest:
            dest[1] = 'f1'
        vars_question.append(flight[1])

    return [vars_question, flight, source, dest, arrive, depart, run_time, brand_name]


def construct_procedural_semantics(logical_form_args):
    if not logical_form_args:
        return

    _vars_question, _flight, _source, _dest, _arrive, _depart, _run_time, _brand_name = logical_form_args

    pattern = re.compile('(vn|vj)\d')
    flight_code = _flight[1].upper() \
        if pattern.match(_flight[1]) \
        else '?f1'

    cities_vietnam = ['hồ chí minh', 'huế', 'hà nội', 'đà nẵng', 'hải phòng', 'khánh hòa']
    city_codes = ['HCM', 'HUE', 'HN', 'ĐN', 'HP', 'KH']

    city1 = city_codes[cities_vietnam.index(_source[2].split('"')[1])]\
        if len(_source) != 0 and _source[2].split('"')[1] in cities_vietnam \
        else '?c1'
    time1 = _depart[2].split('"')[1].upper() \
        if len(_depart) != 0 and re.match("\d+:\d+HR", _depart[2].split('"')[1].upper())\
        else '?t1'
    departure_time = ['DTIME', flight_code, city1, time1]

    city2 = city_codes[cities_vietnam.index(_dest[2].split('"')[1])] \
        if len(_dest) != 0 and _dest[2].split('"')[1] in cities_vietnam \
        else '?c2'
    time2 = _arrive[2].split('"')[1].upper() \
        if len(_arrive) != 0 and re.match("\d+:\d+HR", _arrive[2].split('"')[1].upper())\
        else '?t2'
    arrival_time = ['ATIME', flight_code, city2, time2]

    name_hour = _run_time[2] \
        if len(_run_time) != 0 and (_run_time[2] == 't3' or re.match("\d+:\d+HR", _run_time[2].split('"')[1].upper())) \
        else '?t3'
    time3 = '?t3' if not pattern.match(name_hour) else name_hour
    run_time = ['RUN-TIME', flight_code, city1, city2, time3]

    vars_question = [f'?{x}' for x in _vars_question]

    brand_name = []
    if len(_brand_name) != 0:
        brand_name = ['BRAND-NAME', '?f1', _brand_name[2]]

    return [vars_question, ['FLIGHT', flight_code], arrival_time, departure_time, run_time, brand_name]


def check_flight_name(answer_list, flight_name):
    if flight_name in answer_list.values():
        return flight_name
    else:
        return None


def query_database(database, procedural_semantic_args, is_yes_question, tag_word_list):
    if not procedural_semantic_args:
        return {}

    vars_question, _flight, _arrival_time, _departure_time, _run_time, _brand_name = procedural_semantic_args

    num_of_const = [count_variables(_departure_time),
                    count_variables(_arrival_time),
                    count_variables(_run_time, 1),
                    count_variables(_brand_name) if len(_brand_name) != 0 else 0]
    idx_handle = num_of_const.index(max(num_of_const))
    matches = []

    if idx_handle == 0:  # DTime
        matches = list(filter(lambda x: is_condition_matching(x, _departure_time), database))
    elif idx_handle == 1:  # ATime
        matches = list(filter(lambda x: is_condition_matching(x, _arrival_time), database))
    elif idx_handle == 2:  # Runtime
        matches = list(filter(lambda x: is_condition_matching(x, _run_time), database))
    elif idx_handle == 3:
        query = ['ATIME'] + [*_brand_name]
        matches = list(filter(lambda x: is_condition_matching(x, query, is_query_brand=True), database))

    answers_dict = {}
    for var in vars_question:
        answer = set()
        if var == '?f1':
            answer.update(x[1] for x in matches)
        elif var == '?t1':
            answer.update(x[3] for x in matches if x[0] == 'DTIME')
        elif var == '?t2':
            answer.update(x[3] for x in matches if x[0] == 'ATIME')
        elif var == '?t3':
            answer.update(x[4] for x in matches if x[0] == 'RUN-TIME')
        elif var == '?c2':
            answer.update(x[2] for x in matches if x[0] == 'ATIME')
        answers_dict[var] = list(answer)

    if is_yes_question:
        flight_list_yes_question = []
        for elem in tag_word_list:
            if elem[0] == 'FLIGHT-NAME':
                flight_list_yes_question.append(check_flight_name(answers_dict, elem[1].upper()))
        if flight_list_yes_question != [None]:
            answers_dict = {'?y1': 'Yes'}
        else:
            answers_dict = {'?y2': 'No'}

    return answers_dict
