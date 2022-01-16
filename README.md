# Vaccine-Priority
A short project about the priority of getting a vaccine. The algorithm will prioritize the population over the age of 50 with first priority for vaccination. All other people on the list will be prioritized in the order of their ID. If a country with a low priority is entered, in each of the two groups people from that country will be given a lower priority respectively. In addition, if IDs of people who have already been vaccinated have been entered, the system will filter them out of priority. 

## Dependences
- **Python version**: 3.8
- **installation**: 
	- ast
	- requests
- **Api Reference**:
	- Both Agify.io and Nationalize.io endpoints have a limit of 1000 calls per-day. To increase that, you shoud add a payment. 	

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

## Tests
- Add an entry of person with oldest age but with low priority country id
- Add an entry of young person (age < 50), with the biggest id but with country id which not have low priority.
- Add ids from the elder population entry and the young as well to the vaccinated_ids.csv 
