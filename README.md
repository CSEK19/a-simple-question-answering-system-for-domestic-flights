# Natural Language Processing (CO3085) Assignment

## Personal Information

Student Name: Tran Tien Phat. \
Semester HK222 at Ho Chi Minh City University of Technology.

## Directory Information

- **`Input`**: The input includes a `queries.txt` file containing 10 queries, a `database.txt` file, and a `dictionary.py file for building the database.
- **`Models`**: The model comprises 3 sub-modules, namely:
  - `models.py`: The module implements the models for the assignment. Including:
    - `extract_tagged_words()`: to analyze a query and extract tagged words based on a predefined tag dictionary.
    - `build_dependency_relations()`: to build dependency relations between tagged words based on a set of predefined rules.
    - `build_grammatical_relations()`: to build grammatical relations.
    - `construct_logical_form()`: to construct logical forms from grammatical relations.
    - `construct_procedural_semantics()`: to construct procedural semantics from logical forms.
  - `output.py`: The module prints different types of outputs based on input data.
  - `utils.py`: The module defines several utility functions.
- **`Output`**: The folder contains the results for each query in the `Input` folder.

## Getting Started

### Create and activate virtual environment

```
virtualenv venv
source ./venv/bin/activate
```

### Install required library

```
pip install -r requirement.txt
```

## Usage

### To run the program:

```
python main.py
```
