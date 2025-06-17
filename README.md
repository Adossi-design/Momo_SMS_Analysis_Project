# MTN MoMo SMS Analytics Dashboard

## What I built and why

I built this project as my Enterprise Web Development assignment at African Leadership University. The idea came from a simple observation: I had hundreds of MTN MoMo SMS messages sitting in my phone and no easy way to understand what they were telling me about my own spending. I decided to turn those messages into a proper analytics dashboard that I could actually use to see where my money was going, how much I was receiving, and how my transaction activity changed from month to month.

The system I built takes a raw XML export of my SMS messages, reads through every single one of them, pulls out the financial details using pattern matching, stores everything in a database, and then shows it all on a clean and interactive web dashboard that works on any screen size.

## What the dashboard does

I managed to parse 1,570 out of 1,691 messages, which is a 92.8 percent success rate across seven different transaction types. The dashboard shows me four key numbers at the top of the page: how many transactions I have in total, what the total amount of money involved is, what my single biggest transaction was, and what my average transaction looks like. Those numbers count up from zero when the page loads which I think makes it feel a lot more alive.

I can click on any of the category buttons to filter the table down to just that type of transaction. I can also type in the search box and the results update automatically as I slow down typing, without having to press any button. There are three charts on the page: one that compares the total volume by transaction type, one that shows how my transaction activity changed each month, and one that shows the percentage breakdown of all my categories. I can export everything to a CSV file with one click, and the file opens cleanly in Excel. I can also switch between a dark theme and a light theme and the dashboard remembers my choice the next time I open it.

## The seven transaction types I handled

I wrote patterns to recognise seven different kinds of MTN MoMo messages. Incoming Money is when someone sends money to my account. Payment is when I pay a merchant. Bank Deposit is when money comes in from a linked bank account. Peer Transfer is when I send money to another MoMo user. Airtime Purchase is when I top up mobile airtime. Cash Withdrawal is when I take out cash at an agent. Direct Payment is when a merchant pulls money from my account directly.

## What I used to build it

I used Python with Flask to build the backend API and serve the dashboard. I used SQLite as the database because it is simple, fast, and requires no setup. For the frontend I used plain HTML, CSS, and JavaScript without any heavy framework, plus Chart.js for the three chart visualisations. I loaded the Inter font from Google Fonts to get a clean and professional look.

## How the project is organised

```
Momo_SMS_Analysis_Project/
├── backend/
│   ├── app.py              The Flask server that runs the API and serves the dashboard
│   ├── process_sms.py      The script I wrote to parse the SMS messages into JSON
│   └── insert_data.py      The script that loads the parsed data into the database
├── frontend/
│   ├── index.html          The HTML structure of the dashboard
│   ├── styles.css          All the styling including dark and light themes
│   └── script.js           All the interactivity including charts and search and export
├── DataWorld/Data/
│   └── modified_sms_v2.xml The original SMS backup file with 1691 messages
├── requirements.txt
├── REPORT.md
└── README.md
```

The database file and the intermediate JSON file are not stored in the repository because they are generated each time the pipeline runs. The .gitignore file makes sure they stay out of version control.

## The five API endpoints I built

| Endpoint | What it does |
|---|---|
| GET / | Opens the dashboard in the browser |
| GET /api/transactions | Returns paginated transactions, accepts page and per_page and type as parameters |
| GET /api/search | Searches across the type and party and amount fields and returns matching records |
| GET /api/summary | Returns totals grouped by category and by month so the charts can draw themselves |
| GET /api/stats | Returns the total count and total volume and largest and average transaction in one query |

## How to run the project

First install the two Python packages the project needs.

```bash
pip install -r requirements.txt
```

Then run the SMS parser from inside the backend folder. This reads the XML file and writes a cleaned JSON file.

```bash
cd backend
python process_sms.py
```

Then run the database loader. This takes the JSON file and puts everything into SQLite. It is safe to run this more than once because it clears the old data before loading the new data each time.

```bash
python insert_data.py
```

Finally start the Flask server. Once it is running, open a browser and go to http://localhost:5000 to see the dashboard.

```bash
python app.py
```

If port 5000 is already taken on your machine you can start the server on a different port, for example by running PORT=5001 python app.py and then opening http://localhost:5001 instead.

## About me

Adossi Fred William
African Leadership University, Software Engineering, June 2025
