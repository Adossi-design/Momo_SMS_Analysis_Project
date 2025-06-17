"""
SMS parsing pipeline: reads MTN MoMo XML backup and extracts structured transactions.

Usage:
    python process_sms.py [xml_path] [output_json]
"""
from __future__ import annotations

import json
import logging
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Transaction ID extraction — three formats present in the SMS corpus:
#   "Financial Transaction Id: 76662021700"
#   "TxId: 73214484437."
#   "*162*TxId:13913173274*S*"
_TXID_RE = re.compile(
    r'(?:Financial Transaction Id|TxId)[:\s*]+(\d{8,})',
    re.IGNORECASE,
)

def _extract_txid(body: str) -> str:
    m = _TXID_RE.search(body)
    return m.group(1) if m else None


# Each tuple: (human label, compiled pattern with named groups, default party when regex has none)
# Named groups used: amount, party (optional), date
PATTERNS = [
    (
        "Incoming Money",
        re.compile(
            r"You have received (?P<amount>[\d,]+) RWF from (?P<party>.+?) \(.+?\)"
            r" on your mobile money account at (?P<date>[\d\-: ]+)",
            re.IGNORECASE,
        ),
        None,
    ),
    (
        "Payment",
        re.compile(
            r"Your payment of (?P<amount>[\d,]+) RWF to (?P<party>.+?) \d+ has been completed at (?P<date>[\d\-: ]+)",
            re.IGNORECASE,
        ),
        None,
    ),
    (
        "Airtime Purchase",
        # Original regex had (?:,\d{3}) without * — fixed here; party is always "Airtime"
        re.compile(
            r"Your payment of (?P<amount>[\d,]+) RWF to Airtime\b.+?completed.+?at (?P<date>[\d\-: ]+)",
            re.IGNORECASE,
        ),
        "Airtime",
    ),
    (
        "Bank Deposit",
        re.compile(
            r"(?:A )?bank deposit of (?P<amount>[\d,]+) RWF has been added to your mobile money account at (?P<date>[\d\-: ]+)",
            re.IGNORECASE,
        ),
        "Bank",
    ),
    (
        "Peer Transfer",
        # Original regex had (?:,\d{3}) without * and \(.?\) which only matched 1 char — both fixed
        re.compile(
            r"(?P<amount>[\d,]+) RWF transferred to (?P<party>.+?) \(.+?\) from .* at (?P<date>[\d\-: ]+)",
            re.IGNORECASE,
        ),
        None,
    ),
    (
        "Cash Withdrawal",
        re.compile(
            r"You have withdrawn (?P<amount>[\d,]+) RWF.+?at (?P<date>[\d\-: ]+)",
            re.IGNORECASE,
        ),
        "Agent",
    ),
    (
        "Direct Payment",
        re.compile(
            r"(?:A )?transaction of (?P<amount>[\d,]+) RWF by (?P<party>.+?) (?:has been|was) completed at (?P<date>[\d\-: ]+)",
            re.IGNORECASE,
        ),
        None,
    ),
]


def _parse_amount(raw: str) -> int:
    return int(raw.replace(",", ""))


def _parse_date(raw: str) -> str:
    try:
        return datetime.strptime(raw.strip(), "%Y-%m-%d %H:%M:%S").isoformat()
    except ValueError:
        logger.debug("Unparseable date: %r", raw)
        return None


def parse_sms(body: str) -> dict:
    for label, pattern, default_party in PATTERNS:
        m = pattern.search(body)
        if m is None:
            continue
        groups = m.groupdict()
        party = (groups.get("party") or "").strip() or default_party or "N/A"
        return {
            "type": label,
            "amount": _parse_amount(groups["amount"]),
            "party": party,
            "tx_id": _extract_txid(body),
            "date": _parse_date(groups["date"]),
        }
    return None


def process_xml(xml_path: Path, output_json: Path) -> tuple:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    records = []
    skipped = 0

    for sms in root.findall("sms"):
        body = (sms.attrib.get("body") or "").strip()
        if not body:
            continue
        parsed = parse_sms(body)
        if parsed:
            records.append(parsed)
        else:
            skipped += 1
            logger.debug("Unmatched SMS: %.150s", body)

    output_json.write_text(
        json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return len(records), skipped


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler("unprocessed_messages.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    args = sys.argv[1:]
    base = Path(__file__).parent
    xml_path = Path(args[0]) if args else base.parent / "DataWorld" / "Data" / "modified_sms_v2.xml"
    json_path = Path(args[1]) if len(args) > 1 else base / "cleaned_data.json"

    if not xml_path.exists():
        logger.error("XML file not found: %s", xml_path)
        sys.exit(1)

    matched, skipped = process_xml(xml_path, json_path)
    total = matched + skipped
    logger.info(
        "Parsed %d/%d SMS (%.1f%% matched) -> %s",
        matched,
        total,
        100 * matched / total if total else 0,
        json_path,
    )


if __name__ == "__main__":
    main()
