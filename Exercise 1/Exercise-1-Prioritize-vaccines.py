# ----------------------- FIX THE DICTIONARIES LIST -----------------------
# TODO: write a func that runs over the list of dicts, the func creates a dict that the key is country
#  and the value is list of tuples of {id, name}.

# TODO: write a func that gets the countries_sorted_dct and for each key creates
#  params dct which contains {country_id: country, name: asaf, name: noa}

# TODO: write a func that gets an name and return the most likely country from.

# TODO: write a function that run over the ages,
#  if unknown, check if there is a name, if True, call the name_api func.

# TODO: write a function that run over the countries,
#  if unknown, check if there is a name, if True, call the country_api func.

# TODO: write a func that sorting the
# --------------------------------------------------------------

# TODO: write a func which implement the vaccine sorting algorithm and return a prioritize list.

# TODO:


# IMPORTS
import requests
import os
import ast

# CONSTANT
current_dir = os.path.dirname(__file__)
DATA_FILE_PATH = rf"{current_dir}\resource\data.txt"


def get_data_from_file():
    with open(DATA_FILE_PATH, 'r', encoding='UTF-8') as data_f:
        lines_lst = data_f.readlines()
        return lines_lst


def format_data_to_lst(lines_lst):
    by_lines_without_invalid_chars = [
        "{" + line.split('\n')[:-1][0].replace("“", "'")  # reorganize to str like dicts for ast.literal_eval
            .replace("”", "'")
            .replace("Id", "'Id'")
            .replace("Name", "'Name'")
            .replace("Age", "'Age'")
            .replace("CountryID", "'CountryID'")
            .replace("(Unknown)", "'(Unknown)'")
            .replace("age", "'Age'") + "}"
        for line in lines_lst]

    converted_to_dicts = [ast.literal_eval(dct) for dct in by_lines_without_invalid_chars]
    return converted_to_dicts


def create_dct_of_names_by_country(lst_of_dicts):
    names_by_countries = {}
    dicts_gen = (dct for dct in lst_of_dicts)

    for dct_i in range(len(lst_of_dicts)):
        current_dct = next(dicts_gen)
        if current_dct['Age'] == '(Unknown)' and current_dct['Name'] != '(Unknown)'\
                and current_dct["Name"].isnumeric() is False:

            if current_dct['CountryID'] not in names_by_countries:
                names_by_countries[current_dct['CountryID']] = [(current_dct['Id'], current_dct['Name'])]
            else:
                names_by_countries[current_dct['CountryID']].append((current_dct['Id'], current_dct['Name']))
    return names_by_countries


lines_lst = get_data_from_file()
list_of_dicts = format_data_to_lst(lines_lst)
print(create_dct_of_names_by_country(list_of_dicts))
