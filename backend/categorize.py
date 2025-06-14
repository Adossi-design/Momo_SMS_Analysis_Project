import json
import re
import os

# Paths
parsed_sms_path = os.path.join("backend", "parsed_sms.json")
categorized_path = os.path.join("backend", "categorized_sms.json")
unrecognized_log_path = os.path.join("backend", "unrecognized_log.txt")

# Load parsed messages
with open(parsed_sms_path, "r", encoding="utf-8") as f:
    messages = json.load(f)

categorized = []
unrecognized = []

# Regex patterns for common transaction types
patterns = {
    "incoming_money": re.compile(r"received\s+([0-9,]+)\s*RWF", re.IGNORECASE),
    "payment_to_code_holder": re.compile(r"payment\s+of\s+([0-9,]+)\s*RWF\s+to.*code", re.IGNORECASE),
    "mobile_transfer": re.compile(r"transfer(?:red)?\s+to.*([0-9,]+)\s*RWF", re.IGNORECASE),
    "bank_deposit": re.compile(r"deposit.*([0-9,]+)\s*RWF", re.IGNORECASE),
    "airtime_purchase": re.compile(r"airtime.*([0-9,]+)\s*RWF", re.IGNORECASE),
    "cashpower": re.compile(r"cash\s*power.*([0-9,]+)\s*RWF", re.IGNORECASE),
    "third_party": re.compile(r"initiated\s+by\s+.*third\s+party", re.IGNORECASE),
    "withdrawal_agent": re.compile(r"withdrawn\s+([0-9,]+)\s*RWF.*via\s+agent", re.IGNORECASE),
    "bank_transfer": re.compile(r"transfer.bank.([0-9,]+)\s*RWF", re.IGNORECASE),
    "bundle_purchase": re.compile(r"purchased.bundle.([0-9,]+)\s*RWF", re.IGNORECASE),
}

def categorize_message(body):
    for category, pattern in patterns.items():
        if pattern.search(body):
            return category
    return None

# Categorize messages
for msg in messages:
    body = msg.get("body", "")
    category = categorize_message(body)
    if category:
        categorized.append({
            "body": body,
            "category": category
        })
    else:
        unrecognized.append(body)

# Save categorized messages
with open(categorized_path, "w", encoding="utf-8") as f:
    json.dump(categorized, f, indent=2)

# Save unrecognized messages
with open(unrecognized_log_path, "w", encoding="utf-8") as log_file:
    for line in unrecognized:
        log_file.write(line + "\n")

print(f"[INFO] Successfully categorized {len(categorized)} messages.")
print(f"[INFO] Ignored or unrecognized: {len(unrecognized)} messages (logged in backend/unrecognized_log.txt)")
