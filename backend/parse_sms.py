import xml.etree.ElementTree as ET
import json
import os

# File paths
xml_file_path = "data/modified_sms_v2.xml"
output_json_path = "backend/parsed_sms.json"

# Parse the XML
tree = ET.parse(xml_file_path)
root = tree.getroot()

parsed_data = []

# Extract SMS data from XML
for sms in root.findall("sms"):
    message = {
        "date": sms.get("date"),
        "address": sms.get("address"),
        "body": sms.get("body")
    }
    parsed_data.append(message)

# Save parsed messages to JSON file
with open(output_json_path, "w", encoding="utf-8") as f:
    json.dump(parsed_data, f, indent=2, ensure_ascii=False)

# Print how many messages were parsed
print(f"Parsed {len(parsed_data)} messages from {xml_file_path}")
