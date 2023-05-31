import glob
import os
from Models.models import normalize_city_word, extract_tagged_words, build_dependency_relations, build_grammatical_relations
from Models.models import construct_logical_form, construct_procedural_semantics, query_database
from Models.output import print_relation, print_grammatical_relations, print_logical_form, print_procedural_semantic, print_output


def read_file(file_path):
    with open(file_path, 'r', encoding="utf8") as file:
        content = file.read()
    return content


def write_file(file_path, content):
    with open(file_path, 'w', encoding="utf8") as file:
        file.write(content)


def remove_files(file_path):
    files = glob.glob(file_path)
    for f in files:
        os.remove(f)


def main():
    input_path = os.path.join(os.path.dirname(__file__), 'Input', 'queries.txt')  
    with open(input_path, 'r') as file:
        queries = file.read().split('\n')
    queries = [normalize_city_word(query) for query in queries]

    database_path = os.path.join(os.path.dirname(__file__), 'Input','database.txt')
    with open(database_path, 'r') as file:
        database_file = file.read().split('\n')
    database_file = [record.strip().replace('(', '').replace(')', '').split(' ') for record in database_file]

    remove_files('Output/*')

    i = 1
    output_folder = "Output"

    for query in queries:
        tag_word_list, is_yes_question = extract_tagged_words(query)
        relations = build_dependency_relations(tag_word_list)
        grammatical_relations = build_grammatical_relations(relations)
        logical_form = construct_logical_form(relations, grammatical_relations)
        procedural_semantic = construct_procedural_semantics(logical_form)
        result = query_database(database_file, procedural_semantic, is_yes_question, tag_word_list)

        # Construct the output query content
        output_content = f"""Query {i:04d}: {query}
    
----- Dependency Parsing -----
{print_relation(relations)}

----- Grammatical Relations -----
{print_grammatical_relations(grammatical_relations)}

----- Logical Form -----
{print_logical_form(logical_form)}

----- Procedural Semantic -----
{print_procedural_semantic(procedural_semantic)}

----- Output -----
{print_output(result)}
"""

        output_path = f"{output_folder}/output_query_{i:04d}.txt"
        write_file(output_path, output_content)
        i += 1

    if i <= 2:
        print(f'Successful! {i - 1} output file have been saved in the {output_folder} folder.')
    else:
        print(f'Successful! {i - 1} output files have been saved in the {output_folder} folder.')


if __name__ == '__main__':
    main()
