
# IMPORTS
import requests
import os
import ast
import csv

# CONSTANT
current_dir = os.path.dirname(__file__)
DATA_FILE_PATH = rf"{current_dir}\Database\data.txt"
VACCINATED_IDS_F = rf"{current_dir}\Database\vaccinated_ids.csv"
LOW_PRIORITY_COUNTRIES_IDS_F = rf"{current_dir}\Database\low_priority_countries_ids.csv"
NATIONALIZE_ENDPOINT = r"https://api.nationalize.io/"
AGIFY_ENDPOINT = r"https://api.agify.io/"


def get_data_from_file():
    """Reads the data.txt file's lines. Return list of lines"""

    try:
        with open(DATA_FILE_PATH, 'r', encoding='UTF-8') as data_f:
            lines_lst = data_f.readlines()
            return lines_lst

    except FileNotFoundError:
        print(r"The data file '\Database\data.txt' is missing or moved")
        exit()


def format_data_to_lst(lines_lst):
    """Reformat the lines without invalid signs, convert each line to dictionary, Return list of dictionaries"""

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


def create_dct_of_names_without_countries(lst_of_dicts):
    """"""
    unknown_country_names = {}
    dcts_gen = (dct for dct in lst_of_dicts)
    for dct_i in dcts_gen:
        if dct_i['CountryID'] == '(Unknown)' and dct_i['Name'] != '(Unknown)':
            unknown_country_names[dct_i['Id']] = dct_i['Name']
    return unknown_country_names


def request_for_countries(dct_of_name):
    params = {'name': [name for name in dct_of_name.values()]}
    res = requests.get(NATIONALIZE_ENDPOINT, params=params)
    return res.json()


def analysed_best_country_for_name(name_country_json):
    best_probability = {}

    for name in name_country_json:
        compare = (None, 0)
        for country in name['country']:
            if country['probability'] > compare[1]:
                compare = (country['country_id'], country['probability'])

        # keep all unfilled values as same in case there isn't any match
        if compare[0] is not None:
            best_probability[name['name']] = compare[0]
        else:
            best_probability[name['name']] = '(Unknown)'
    return best_probability


def fill_the_unknown_countries(lst_of_dcts, best_probability_dct):
    lst_of_dcts_gen = (dct for dct in lst_of_dcts)
    for dct in lst_of_dcts_gen:
        if dct['CountryID'] == '(Unknown)' and dct['Name'] in best_probability_dct:
            dct['CountryID'] = best_probability_dct[dct['Name']]
    return lst_of_dcts


def create_dct_of_names_by_country(lst_of_dicts):
    names_by_countries = {}
    dicts_gen = (dct for dct in lst_of_dicts)
    for dct_i in dicts_gen:
        if dct_i['Age'] == '(Unknown)' and dct_i['Name'] != '(Unknown)'\
                and dct_i["Name"].isnumeric() is False:
            if dct_i['CountryID'] not in names_by_countries:
                names_by_countries[dct_i['CountryID']] = [(dct_i['Id'], dct_i['Name'])]
            else:
                names_by_countries[dct_i['CountryID']].append((dct_i['Id'], dct_i['Name']))
    return names_by_countries


def request_for_ages(dct_of_names_by_country):
    params = {country: [t[1] for t in dct_of_names_by_country[country]] for country in dct_of_names_by_country}
    res_result_lst = []
    for country in params:
        if country != '(Unknown)':
            res = requests.get(AGIFY_ENDPOINT, params={'country_id': country, 'name': params[country]})
        else:
            res = requests.get(AGIFY_ENDPOINT, params={'name': params[country]})
        res_result_lst.append(res.json())
    return res_result_lst


def fill_the_unknown_ages(lst_of_dcts, agify_res_lst):
    agify_res_gen = (dct for dct in agify_res_lst)
    for d in agify_res_gen:
        for dct in lst_of_dcts:
            try:
                if dct['Age'] == '(Unknown)' and dct['Name'] == d['name'] and dct['CountryID'] == d['country_id']:
                    if d['age'] is not None:
                        dct['Age'] = d['age']
                    else:
                        dct['Age'] = '(Unknown)'

            except KeyError:
                if dct['Age'] == '(Unknown)' and dct['Name'] == d['name']:
                    if d['age'] is not None:
                        dct['Age'] = d['age']
                    else:
                        dct['Age'] = '(Unknown)'
    return lst_of_dcts


def prioritize_vaccine(complete_lst_of_dcts):
    return sorted(complete_lst_of_dcts, key=lambda i: i['Age'] if i['Age'] != '(Unknown)' and i['Age'] >= 50
    else -i['Id'], reverse=True)


def already_vaccinated_filter(all_persons_dicts_lst):
    with open(VACCINATED_IDS_F, 'r', encoding='utf-8') as ids_file:
        try:
            if os.path.getsize(VACCINATED_IDS_F) == 2:
                return all_persons_dicts_lst
            else:
                persons_ids = [int(row[0]) for row in csv.reader(ids_file)]
                return list(filter(lambda dct: (dct['Id'] not in persons_ids), all_persons_dicts_lst))

        except ValueError as e:
            print(f"Invalid value{e.args[0].split(':')[-1]} at the vaccinated_ids.csv file.")
            exit()

        except FileNotFoundError:
            print(f"The file {VACCINATED_IDS_F} is missing or moved")
            exit()


def read_countries_file():
    try:
        with open(LOW_PRIORITY_COUNTRIES_IDS_F, 'r', encoding='utf-8') as LPCI_FILE:

            data = csv.reader(LPCI_FILE)
            countries_lst = [row[0] for row in data]

            for c in countries_lst:
                value_check = c.isdigit()
                if value_check:
                    raise ValueError(c)
            return countries_lst

    except FileNotFoundError:
        print(f"The file {LOW_PRIORITY_COUNTRIES_IDS_F} is missing or moved")
        exit()

    except IndexError:
        return []

    except ValueError as e:
        print(f"Invalid value: '{e.args[0].split(':')[-1]}' in the low_priority_countries_id")
        exit()


def reprioritize_by_country(sorted_lst, countries_lst):

    elders_slice = sorted([dct for dct in sorted_lst if dct['Age'] != '(Unknown)' and dct['Age'] >= 50],
                          key=lambda i: (i['Age'] if i['CountryID'] not in countries_lst else 0), reverse=True)

    others_slice = sorted([dct for dct in sorted_lst[::-1] if dct['Age'] == '(Unknown)' or dct['Age'] < 50],
                          key=lambda i: (i['Id'] if i['CountryID'] in countries_lst else 0), reverse=True)[::-1]
    return elders_slice + others_slice


def write_results(final_priority_lst, session_f):
    keys = final_priority_lst[0].keys()
    with open(session_f, 'w') as r_f:
        dict_writer = csv.DictWriter(r_f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(final_priority_lst)


def is_session_n_exist():
    session_n = input("Enter a running session name: ")
    session_f = rf"{current_dir}\Results\{session_n}.csv"

    if os.path.exists(session_f):
        choice = input(f"The session name '{session_n}' is already exist.\n"
                       f"press '1' for change it. otherwise, press any key to overwrite it."
                       f"\n>> ")
        if choice == '1':
            session_n = input("New session name: ")
            return rf"{current_dir}\Results\{session_n}.csv"

        else:
            return session_f
    else:
        return session_f


def main():
    print("""Welcome to the Vaccine Priority Program                           
                     .--.          
            ,-.------+-.|  ,-.     
   0--=======* )"("")===)===* )    
   o        `-"---==-+-"|  `-"     
   0                 '--'   ~JW~  \n""")

    session_result_f = is_session_n_exist()

    # read and format the data
    lines_lst = get_data_from_file()
    list_of_dicts = format_data_to_lst(lines_lst)

    # filter already vaccinated feature
    filtered_people_list = already_vaccinated_filter(list_of_dicts)

    # optimizations of data for efficient api requests, than filling the missing data.
    dcts_of_names_without_country = create_dct_of_names_without_countries(filtered_people_list)
    countries_probability_json = request_for_countries(dcts_of_names_without_country)
    best_probability_of_countries = analysed_best_country_for_name(countries_probability_json)
    countries_filled_lst_of_dcts = fill_the_unknown_countries(filtered_people_list, best_probability_of_countries)
    dct_of_names_by_country = create_dct_of_names_by_country(countries_filled_lst_of_dcts)
    agify_age_lst = request_for_ages(dct_of_names_by_country)
    complete_data = fill_the_unknown_ages(filtered_people_list, agify_age_lst)

    # sorting algorithm
    sorted_proirity_for_vaccine = prioritize_vaccine(complete_data)
    filter_by_countrues = reprioritize_by_country(sorted_proirity_for_vaccine, read_countries_file())
    write_results(filter_by_countrues, session_result_f)
    print("Complete")


if __name__ == '__main__':
    main()