# Vaccine-Priority
A short project about the priority of getting a vaccine.

Python version: 3.8
Dependencies: none any installation required.

## Structure
- **Prioritize-vaccines.py**: The main file to execute for starting the program.
- **Database**: A folder that contains 3 files-
	- data.txt: contains all the lines of people that the program work with.
	- low_priority_countries_ids.csv: contains countire id of countries which get low priority at the sorting algorithm.
	- vaccinated_ids.csv: contains ids of people which already vaccine and will filter out from the sorting algorithm.
- **Results**: A folder that contains the csv files of the results.

## Usage
- Fill up data.txt in the format bellow:  
	- Id: 1, Name: “Gil”, Age: 22, CountryID: “IL” 
- (oprional) Fill up low_priority_countries_ids.csv whith id number from data.txt
- (oprional) Fill up vaccinated_ids.csv with countries id like: IL
- Run the Prioritize-vaccines.py.
- Enter a running session name.
- wait for 'Complete' to print on the screen.
