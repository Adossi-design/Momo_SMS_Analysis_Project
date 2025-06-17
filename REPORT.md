# MTN MoMo SMS Data Analysis: Project Report

Author: Adossi Fred William
University: African Leadership University
Programme: Software Engineering
Course: Enterprise Web Development
Date: June 2025


## 1. Introduction

For this assignment I built a full-stack web application that analyses SMS transaction data from MTN MoMo, which is the mobile money service I use in Rwanda. The idea behind the project is simple: every time I make or receive a payment through MTN MoMo, I get a text message confirming the details. Over time those messages pile up in my inbox and I have no easy way to look back at them and understand my financial activity. I wanted to fix that. So I built a system that reads all those messages automatically, pulls out the useful information from each one, stores everything in a database, and shows it all on a proper analytics dashboard that I can actually use.

MTN MoMo is one of the most popular mobile money platforms in sub-Saharan Africa. Millions of people use it every day to send money, pay for goods, top up airtime, and move money between their bank and their mobile wallet. The SMS messages it sends out are detailed enough to reconstruct a full transaction history if you know how to read them. I figured out the patterns in those messages and wrote code to extract the data automatically.


## 2. What problem I was trying to solve

The main problem I was solving is that my transaction history was sitting in my phone as hundreds of unstructured text messages with no way to search them, filter them, or see any trends. The MTN MoMo app itself does not give me the kind of historical analysis I wanted. I could not easily answer questions like how much I spent on payments last August, or how many times I received money in a given month, or what my average transaction amount looks like.

So I set myself the goal of building a complete pipeline: start from the raw SMS backup file, extract all the transaction details I needed, put them in a database that I could query efficiently, build an API to expose that data in a structured way, and then build a dashboard that makes it easy to explore everything visually. I also wanted the dashboard to look professional and work well on a phone as well as a computer.


## 3. The data I worked with

The data source is an Android SMS backup file in XML format that I exported from my phone. It contains 1,691 messages covering the period from May 2024 to January 2025, which is about nine months of my MTN MoMo activity.

Looking through those messages, I identified seven different types of notification that MTN MoMo sends out. When someone sends me money, the message says something like "You have received a certain amount in RWF from a named person on your mobile money account at a certain date and time". When I pay a merchant, the message starts with a transaction ID and then confirms that my payment of a certain amount to a named business has been completed. When I send money to another MoMo user, the message confirms that a certain amount was transferred to a named person. Bank deposits, airtime purchases, cash withdrawals at agents, and direct payments from merchants each have their own distinct message format that I learned to recognise.

On top of those financial messages, the backup also contains one-time password notifications, promotional messages from MTN, and balance enquiry replies. I did not want those in my dataset so I made sure my system ignores them.


## 4. How I built the data processing pipeline

I split the data processing into two separate Python scripts so that each step could be run and tested independently.

### 4.1 Parsing the SMS messages

The first script, process_sms.py, is where all the pattern matching happens. I used Python's ElementTree library to read the XML file and loop through every message element. For each message I tried to match the body text against seven regular expressions I wrote, one for each transaction type.

I used named capture groups in my regular expressions, meaning I gave each part of the pattern a name like amount or party or date. This made the code much easier to read and debug compared to referencing groups by number. For the amount I wrote a pattern that matches both plain numbers like 1000 and comma-formatted numbers like 1,000 and then strips the commas before converting to an integer. For the date I parsed the format that MoMo uses, which is YYYY-MM-DD HH:MM:SS, and converted it to ISO 8601 format for consistent storage.

I also added a secondary pattern that looks for transaction reference identifiers. MoMo uses three different formats for these: some messages put the ID at the start with a TxId label, some put it at the end with a Financial Transaction Id label, and some embed it inside a USSD shortcode string. My secondary pattern catches all three formats.

Any message that did not match any of my seven patterns gets logged to a file so I could review what I was missing. The final output is a JSON file containing all 1,570 successfully matched records.

### 4.2 Loading into the database

The second script, insert_data.py, reads the JSON file and loads everything into a SQLite database. I designed it to be idempotent, which means I can run it as many times as I want and I always end up with exactly the right data in the database. It does this by deleting all the existing rows first and then inserting the new ones in a single batched operation. If anything goes wrong during the insert, the whole thing rolls back so the database is never left in a broken state.

The database has one table called transactions with columns for the transaction type, the amount as an integer in Rwandan Francs, the counterparty name, the reference identifier which is nullable because not all messages include one, and the date as a text string.


## 5. The API I built

I used Flask to build the backend API and I made one design decision early on that simplified everything: I had Flask serve the dashboard HTML and CSS and JavaScript files directly as static files. This meant I never had to deal with cross-origin issues in the browser and I never had to hardcode any server address in the frontend code. The dashboard just calls its own origin for everything.

I built five endpoints. The transactions endpoint returns a paginated list of records and accepts parameters for the page number, the page size, and an optional category filter that restricts the results to a single transaction type using a SQL WHERE clause. The search endpoint takes a query string and does a partial match across the type, party, and amount columns in the database using SQL LIKE expressions with parameterised placeholders to prevent injection attacks. The summary endpoint runs two GROUP BY queries and returns the totals by category and by month that my chart visualisations need. The stats endpoint runs a single query that returns the total count, total volume, maximum amount, and average amount all at once. I also added proper JSON error responses for 404 and 500 errors so the API behaves consistently in all cases.

For database connections I used Flask's application context object so that each request gets its own connection that is automatically closed when the request finishes.


## 6. The dashboard I designed

The dashboard is a single-page application that loads in the browser. I wanted it to look like something a real company would build, so I put a lot of thought into the visual design. I chose a dark theme as the default because I think it suits a financial analytics tool, and I used MTN's brand yellow as the accent colour throughout. I also built a complete light theme and added a toggle button in the header so the user can switch between them. The chosen theme gets saved in localStorage so it persists across sessions.

For the typography I loaded the Inter font from Google Fonts because it is clean and modern and works well for both headings and body text. I added a subtle dot grid pattern to the background using CSS gradients to give the page some texture without being distracting.

At the top of the page I have four KPI cards. Each one shows a key metric: total transactions, total volume, largest transaction, and average transaction. When the page loads I animate the numbers from zero up to their real values using a cubic ease-out easing function which makes it feel polished. On small screens the four cards stack into two columns and on very small screens they go to one column per row.

Below the KPI cards I have a row of filter chips, one for each transaction category, with the count for that category shown inside the chip. Clicking a chip sends a filtered request to the API and updates the table below to show only that category's transactions. I also have a search input that sends a request to the search endpoint 350 milliseconds after the user stops typing, which means the results update in near-real time without flooding the server with requests on every keystroke. A clear button resets everything back to the full dataset.

The three charts sit side by side on larger screens. I chose a horizontal bar chart for the category volume comparison because the category names are long and they fit much more naturally on horizontal bars than vertical ones. For the monthly trend I used an area line chart with a yellow gradient fill beneath the line because it makes the trend direction very obvious at a glance. For the category distribution I used a doughnut chart because it shows proportions clearly without looking as dated as a plain pie chart. When the user switches themes I destroy all three charts and rebuild them from scratch so that the colours and grid lines and tooltip backgrounds always match the active theme.

The transaction table has a coloured pill badge for each row's category. The colour of the badge matches the colour used for that category everywhere else on the dashboard. Amounts are right-aligned and formatted with thousands separators. Dates are shown in a readable format using the browser's built-in date formatting. When a transaction has no reference ID I show an em dash instead of a word like null.

For pagination I wrote a function that calculates which page numbers to show. It always shows the first and last page, always shows the pages immediately around the current one, and puts ellipsis markers in the gaps. This keeps the pagination row compact no matter how many pages there are.

The export button collects up to 2,000 records from the API, builds a CSV file entirely in JavaScript, adds a byte order mark so Excel reads the character encoding correctly, and saves the file to the user's computer without any server-side processing.


## 7. My results

Out of the 1,691 messages in my backup file I successfully extracted 1,570 transactions, which is a 92.8 percent match rate. I am happy with that number and I know that most of what I missed are one-time password messages and promotional texts that are not financial transactions at all.

Looking at the breakdown by category, I have 659 payment transactions which is 42.0 percent of my total, and 585 peer transfers which is 37.3 percent. Bank deposits account for 248 transactions at 15.8 percent, incoming money for 63 at 4.0 percent, and airtime purchases for 15 at 1.0 percent. My total transaction volume across all categories is 31,280,396 Rwandan Francs. My single biggest transaction was 1,050,000 RWF and my average transaction is 19,923 RWF.

Of my 1,570 records, 737 of them have a verified transaction reference identifier that I extracted from the message text. The other 833 do not have one because those message types simply do not include a reference ID in the text that MoMo sends out.

Looking at the monthly chart, my transaction volume peaked in August 2024 and then settled into a fairly consistent level through the end of the year into January 2025. That kind of trend is something I never would have noticed just scrolling through my SMS inbox.


## 8. Problems I ran into and how I fixed them

The biggest challenge was dealing with how inconsistent the MoMo message formats are. Not all message types follow the same template and some of them changed slightly over the nine months I was looking at. I solved this by using named capture groups in my patterns instead of positional groups, which made it much easier to add new patterns and tweak existing ones without breaking anything else.

The most impactful bug I fixed was in two of my original patterns where I had written a group to match comma-formatted numbers but forgot to add the repetition quantifier that allows multiple comma groups. This meant any amount above 999 in those two categories would fail to match. Fixing that one character in each pattern is what pushed my match rate from around 57 percent up to 92.8 percent.

On the frontend, keeping the chart colours consistent when the user switches themes was trickier than I expected. I tried applying the colours through CSS at first but the Chart.js library uses inline styles for its elements and CSS cannot easily override those. The solution I found was to destroy all three chart instances and rebuild them completely every time the theme changes, passing the new theme colours directly into the chart configuration. It is a bit more work but it works perfectly.

For the pagination I had to think about how to display a manageable number of page buttons when there are hundreds of pages in the dataset. I wrote a function that figures out which page numbers to show based on where the user currently is, always anchors the first and last page, and inserts ellipsis markers wherever there is a gap, so the row never gets longer than seven elements regardless of the total page count.


## 9. Conclusion

I am proud of what I built for this assignment. I started with 1,691 unstructured text messages and ended up with a professional analytics dashboard that gives me real insight into my own financial activity. The technical work covered the full stack: data engineering, SQL database design, REST API development, and modern frontend design with responsive layout and theme support.

Every part of the system is built with practical reliability in mind. The data pipeline can be rerun safely at any time. The API uses parameterised queries throughout to prevent injection attacks. The Flask server handles database connections properly so there are no leaks. The frontend code is organised clearly and handles errors gracefully without crashing the whole page.

I think the most satisfying outcome is that the dashboard genuinely works as a tool I would actually use. It is fast, it looks good, it works on my phone, and it tells me things about my spending that I genuinely did not know before I built it.

African Leadership University, Software Engineering, June 2025.
Adossi Fred William.
