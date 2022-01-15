
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
    """
    The func format the data which comes from data.txt
    It replace invalid signs and convert each line to dictionary.
    :param lines_lst: list of lines of the original data from data.txt
    :return: list of dictionaries

    """

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


def names_lst_without_countries(lst_of_dicts):
    """
    Generate each line of dictionary, check if there is name without CountryID,
    if not add to list.
    :param lst_of_dicts: the formatted list of dicts contains the people data from the data.txt file.
    :return: Return list of names without country

    """
    unknown_country_names = []
    dcts_gen = (dct for dct in lst_of_dicts)
    for dct_i in dcts_gen:
        if dct_i['CountryID'] == '(Unknown)' and dct_i['Name'] != '(Unknown)':
            unknown_country_names.append(dct_i['Name'])
    return unknown_country_names


def request_for_countries(names_lst):
    """
    Check if there are names for api request, request a list of names at once.
    :param names_lst: list contains names which haven't countryID.
    :return: A response as json contains country for each name. / None for no names in names_lst 
    
    """
    if len(names_lst) != 0:
        params = {'name': names_lst}
        res = requests.get(NATIONALIZE_ENDPOINT, params=params)
        if res.status_code != 200:
            print(f"Error in api call to nationalize.io ({res.status_code})")
            exit()
        return res.json()
    else:
        return None


def analysed_best_country_for_name(name_country_json):
    """
    For each name in the json, compare the probability of the country. For name with no match from the api response,
    {name: '(Unknown)'} 
    :param name_country_json: A response as json contains names and countries related to each name. 
    :return: A dict contains {name: most probability of country}
    
    """
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


def fill_unknown_countries(lst_of_dcts, name_country_prob_dct):
    """
    Fill the {... counttryID: '(Unknown)'} of names from the name_country_prob_lst.
    :param lst_of_dcts: List contains the dictionaries of each person form data.txt
    :param name_country_prob_dct: {name: most probability country for the name}
    :return: list of dicts filled with the countries found from the api.

    """
    lst_of_dcts_gen = (dct for dct in lst_of_dcts)
    for dct in lst_of_dcts_gen:
        if dct['CountryID'] == '(Unknown)' and dct['Name'] in name_country_prob_dct:
            dct['CountryID'] = name_country_prob_dct[dct['Name']]
    return lst_of_dcts


def create_names_by_country_dct(lst_of_dicts):
    """
    Create {CountryID: [name1, name2, name3]} from lst_of_dcts for make an efficient api calls.
    :param lst_of_dicts: List contains the dictionaries of each person form data.txt
    :return: a dict of countries and lists of names. {CountryID: [name1, name2, name3]}

    """
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


def request_for_ages(names_by_country_dct):
    """
    Request for nationalize.io api in the most efficient way: multiple names by one country.
    :param names_by_country_dct: {CountryID: [name1, name2, name3]}
    :return: list of response in json format. [{...}, {...}]

    """
    if len(names_by_country_dct) != 0:
        params = {country: [t[1] for t in names_by_country_dct[country]] for country in names_by_country_dct}
        res_result_lst = []
        for country in params:
            if country != '(Unknown)':
                res = requests.get(AGIFY_ENDPOINT, params={'country_id': country, 'name': params[country]})
                print(f"Error in api call to Agify.io ({res.status_code})")
                exit()
            else:
                res = requests.get(AGIFY_ENDPOINT, params={'name': params[country]})
                print(f"Error in api call to Agify.io ({res.status_code})")
                exit()
            res_result_lst.append(res.json())
        return res_result_lst
    else:
        return None


def fill_unknown_ages(lst_of_dcts, agify_res_lst):
    """

    :param lst_of_dcts:  List contains the dictionaries of each person form data.txt
    :param agify_res_lst: A list contains dicts of {name: age}
    :return: lst of dicts of the persons which filled with the ages of the known names which had '(Unknown)' age.
    """
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
    """
    re-order the list of dictionaries by age (oldest at the start) for all the dicts which Age >= 50.
    All the others dicts order by ID number (smallest at the start)
    :param complete_lst_of_dcts: A list of dicts of all the people from data.txt after filling ages and countries.
    :return: sorted lst_of_dcts

    """
    return sorted(complete_lst_of_dcts, key=lambda i: i['Age'] if i['Age'] != '(Unknown)' and i['Age'] >= 50
    else -i['Id'], reverse=True)


def already_vaccinated_filter(all_persons_dicts_lst):
    """
    Read the VACCINATED_IDS_F file and filter out all the Id's in the lst_of_dcts by the Id's from the file.
    :param all_persons_dicts_lst: List contains the dictionaries of each person form data.txt
    :return: lst_of_dcts

    """
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
    """Read the LOW_PRIORITY_COUNTRIES_IDS_F file. Return list of countries."""
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
    """
    Sort all dicts which dct['Age'] >= 50 so dicts with country in countries_lst will be at the bottom of the list.
    The same sort happens for all the others dicts which dct['Age'] < 50 or dct['Age'] == '(Unknown)' by dct['Id'].
    :param sorted_lst: list of dicts which already order by age and id.
    :param countries_lst: List of countries id which have low priority.
    :return: list of dicts re-order.

    """
    elders_slice = sorted([dct for dct in sorted_lst if dct['Age'] != '(Unknown)' and dct['Age'] >= 50],
                          key=lambda i: (i['Age'] if i['CountryID'] not in countries_lst else 0), reverse=True)

    others_slice = sorted([dct for dct in sorted_lst[::-1] if dct['Age'] == '(Unknown)' or dct['Age'] < 50],
                          key=lambda i: (i['Id'] if i['CountryID'] in countries_lst else 0), reverse=True)[::-1]
    return elders_slice + others_slice


def write_results(final_priority_lst, session_f):
    """
    Create a csv file contains 4 columns: Id, Name, Age, CountryID. Each row represent a person from final_priority_lst
    :param final_priority_lst: List of dicts after all the sorts and the filters.
    :param session_f: path of the result file.
    :return: None
    """
    keys = final_priority_lst[0].keys()
    with open(session_f, 'w') as r_f:
        dict_writer = csv.DictWriter(r_f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(final_priority_lst)


def is_session_n_exist():
    """
    Get a name for the running session from the user, check if the name already exist
    (if exist let the user choose again). Return result file path.
    :return: path of the csv result file.

    """
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


def sorting_algo(complete_data, session_result_f):
    """
    Run prioritize_vaccine() and then reprioritize_by_country(), than run write_results().
    :param complete_data: list of dicts contains all the people from data.txt after
    filling most of the '(Unknown)' values.
    :param session_result_f: result file path.
    :return: None
    """
    age_id_prio_sort = prioritize_vaccine(complete_data)
    low_prio_countries_filter = reprioritize_by_country(age_id_prio_sort, read_countries_file())
    write_results(low_prio_countries_filter, session_result_f)
    print("Complete")


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
    names_lst = names_lst_without_countries(filtered_people_list)
    if names_lst is not None:
        countries_probability_json = request_for_countries(names_lst)
        best_prob_countries = analysed_best_country_for_name(countries_probability_json)
        countries_filled_lst_of_dcts = fill_unknown_countries(filtered_people_list, best_prob_countries)
        names_by_country_dct = create_names_by_country_dct(countries_filled_lst_of_dcts)
        agify_age_lst = request_for_ages(names_by_country_dct)
        if agify_age_lst is not None:
            complete_data = fill_unknown_ages(filtered_people_list, agify_age_lst)
            sorting_algo(complete_data, session_result_f)
        else:  # in case all the people have age value.
            sorting_algo(filtered_people_list, session_result_f)

    else:  # in case all the people have country value
        names_by_country_dct = create_names_by_country_dct(filtered_people_list)
        agify_age_lst = request_for_ages(names_by_country_dct)
        if agify_age_lst is not None:
            complete_data = fill_unknown_ages(filtered_people_list, agify_age_lst)
            sorting_algo(complete_data, session_result_f)
        else:
            sorting_algo(filtered_people_list, session_result_f)
            

if __name__ == '__main__':
    main()
