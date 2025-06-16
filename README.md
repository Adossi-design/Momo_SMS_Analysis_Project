# MTN MoMo SMS Data Analysis Dashboard

## Project Overview
This is an Enterprise Web Development assignment developed by Adossi Fred William as part of the Software Engineering program at African Leadership University. The project analyzes SMS data from MTN MoMo Rwanda by extracting, cleaning, categorizing, and storing it in a relational database.

## Features
- Parses over 1600 MoMo SMS messages
- Categorizes into multiple types (Incoming Money, Payment, Bank Deposit, Peer Transfer, etc.)
- Stores in a normalized SQLite database
- Backend API built using Flask
- Interactive, responsive dashboard using HTML, CSS, JavaScript, and Chart.js
- Distinctive chart colors per category
- Real-time search and filter functionality
- Logs unprocessed/ignored messages

## Technologies Used
- **Backend:** Python, Flask
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript, Chart.js
- **Data Source:** XML
- **Note** Make sure these tech are install on computer and terminal before run the codes
## Bonus (API Integration)
Flask-based RESTful API:
- `GET /api/transactions`: All transactions
- `GET /api/search?query=...`: Filtered results
- `GET /api/summary`: Summary data for charts

## 📂 Folder Structure
```
├── backend/
│   ├── app.py
│   ├── process_sms.py
│   ├── insert_data.py
│   ├── db.sqlite3
│   └── unprocessed_messages.log
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── script.js
├── DataWorld/Data/
│   └── modified_sms_v2.xml
├── docs/
│   ├── report.pdf
│   ├── README.md
│   ├── AUTHORS
│   └── test_log.txt
```

## How to Run the Project

1. Process XML:
```bash
cd backend
python process_sms.py
```

2. Insert into database:
```bash
python insert_data.py
```

3. Start the Flask server:
```bash
python app.py
```

4. Open `frontend/index.html` in a browser (ensure backend is running).

##  Author
Adossi Fred William

## 🎥 Video
[https://drive.google.com/file/d/1QO8ePBLxgExcZPUWK6BE4l22Rsr5OCAg/view?usp=sharing]
