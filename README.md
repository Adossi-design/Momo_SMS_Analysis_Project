# MoMo Data Analysis Project

This is an Enterprise Web Development assignment developed by Adossi Fred William as part of the Software Engineering program at African Leadership University. The project analyzes SMS data from MTN MoMo Rwanda by extracting, cleaning, categorizing, and storing it in a relational database. 

## Features

-  Clean parsing of raw MoMo XML SMS data  
-  Smart categorization by transaction type (deposit, withdrawal, etc.)  
-  Automatic SQLite database creation  
-  Flask API for dynamic data queries (Bonus)  
-  Modern, responsive frontend dashboard  
-  Real-time search with autocomplete  
-  Interactive charts using Chart.js  
-  Clean project structure and modular code  
-  Follows all ALU SFS assignment instructions  

## Technologies Used

- *Python 3.10+*  
- *Flask*  
- *SQLite3*  
- *HTML5 + CSS3 + JavaScript*  
- *Chart.js*  
- *XML Parsing (ElementTree)*  
- *Responsive Flex/Grid Layout*  

## Project Structure

```plaintext
MoMo_SMS_Analysis_Project/
│
├── backend/
│   ├── parse_sms.py         
│   ├── categorize.py         
│   ├── insert_to_db.py       
│   ├── api.py                
│   └── sms.db               
│
├── data/
│   └── modified_sms_v2.xml  
│
├── frontend/
│   ├── index.html            
│   ├── style.css            
│   └── script.js             
│
├── test_log.txt             
├── README.md                 
├── AUTHOR                    
├── REPORT.pdf
├── momo_sms_analysis_project.zip
```
## Setup instructions

```bash
# 1. Clone the repository
git clone https://github.com/Adossi-design/MoMo_SMS_Analysis_Project.git
cd MoMo_SMS_Analysis_Project

# 2. Install Flask
pip install flask

# 3. Parse and extract SMS data
python3 backend/parse_sms.py

# 4. Categorize each transaction
python3 backend/categorize.py

# 5. Run the backend parser and DB inserter
python3 backend/insert_to_db.py

# 6. Start the Flask API
python3 backend/api.py
```
Open your browser and go to frontend/index.html to view the dashboard.

## How to Use the Project
	1.	Open frontend/index.html in your browser.
	2.	Use the dropdown menu to filter by category (e.g. Deposit, Withdrawal).
	3.	Type in the search bar to filter using real-time suggestions.
	4.	View dynamic visualizations that auto-update based on filters.
	5.	Hover or click on chart segments to see totals and transaction types.
	6.	Scroll the transaction table to view full transaction details.

## Visualizations 
	•	 Bar Chart – Transactions by Category
	•	 Line Chart – Monthly Transaction Trend
	•	 Pie Chart – Deposit vs Withdrawal Proportion
	•	 Data Table – Filterable, searchable list of all transactions

## Walkthrough Video

A complete 5-minute demo video has been recorded.
The video covers:
	•	Project overview and objectives
	•	How the backend extracts and cleans the data
	•	API routes and integration
	•	Live dashboard interaction and filtering
	•	Mobile responsiveness in action

 Watch here: [Insert Your Video Link]
### Testing

Refer to test_log.txt for output logs of all backend scripts and API tests. This file proves that all scripts execute successfully and the database is functional.


