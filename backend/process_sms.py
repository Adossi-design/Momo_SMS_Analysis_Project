import xml.etree.ElementTree as ET
import re
import json
import logging
from datetime import datetime

logging.basicConfig(filename='unprocessed_messages.log', level=logging.INFO)

# Updated regex patterns based on your actual messages
CATEGORIES = {
    "received": r"You have received (\d{1,3}(?:,\d{3})*|\d+) RWF from (.+?) \(.+?\) on your mobile money account at ([\d\-: ]+)",
    "payment": r"Your payment of (\d{1,3}(?:,\d{3})*|\d+) RWF to (.+?) \d+ has been completed at ([\d\-: ]+)",
    "airtime": r"Your payment of (\d{1,3}(?:,\d{3})|\d+) RWF to Airtime . completed .* at ([\d\-: ]+)",
    "bank": r"bank deposit of (\d{1,3}(?:,\d{3})*|\d+) RWF has been added to your mobile money account at ([\d\-: ]+)",
    "transfer": r"(\d{1,3}(?:,\d{3})|\d+) RWF transferred to (.+?) \(.?\) from .* at ([\d\-: ]+)",
}

def parse_sms_body(body):
    for category, pattern in CATEGORIES.items():
        match = re.search(pattern, body)
        if match:
            return extract_fields(category, match)
    logging.info(f"Ignored SMS: {body}")
    return None

def extract_fields(category, match):
    if category == "received":
        amount, sender, date = match.groups()
        return {
            "type": "Incoming Money",
            "amount": int(amount.replace(',', '')),
            "party": sender,
            "tx_id": None,
            "date": format_date(date)
        }
    elif category == "payment":
        amount, receiver, date = match.groups()
        return {
            "type": "Payment",
            "amount": int(amount.replace(',', '')),
            "party": receiver,
            "tx_id": None,
            "date": format_date(date)
        }
    elif category == "airtime":
        amount, date = match.groups()
        return {
            "type": "Airtime Purchase",
            "amount": int(amount.replace(',', '')),
            "party": "Airtime",
            "tx_id": None,
            "date": format_date(date)
        }
    elif category == "bank":
        amount, date = match.groups()
        return {
            "type": "Bank Deposit",
            "amount": int(amount.replace(',', '')),
            "party": "Bank",
            "tx_id": None,
            "date": format_date(date)
        }
    elif category == "transfer":
        amount, receiver, date = match.groups()
        return {
            "type": "Peer Transfer",
            "amount": int(amount.replace(',', '')),
            "party": receiver,
            "tx_id": None,
            "date": format_date(date)
        }
    return None

def format_date(raw_date):
    try:
        return datetime.strptime(raw_date.strip(), "%Y-%m-%d %H:%M:%S").isoformat()
    except Exception:
        return None

def process_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    records = []

    for sms in root.findall('sms'):
        body = sms.attrib.get('body')
        if not body:
            continue

        parsed = parse_sms_body(body.strip())
        if parsed:
            records.append(parsed)

    with open('cleaned_data.json', 'w') as f:
        json.dump(records, f, indent=4)

    print(f"Processed {len(records)} valid messages.")

if __name__ == "__main__":
    process_xml("../DataWorld/Data/modified_sms_v2.xml")
