"""
Script 1: RPA-Style Eligibility Checker
H9IAPA - Clothing Returns Automation
Mimics RPA bot behaviour: reads Excel, applies business rules, writes results back.
"""

import openpyxl
from datetime import datetime
import logging
import os

LOG_FILE = os.path.join(os.path.dirname(__file__), "returns_log.txt")
EXCEL_FILE = os.path.join(os.path.dirname(__file__), "data", "Returns_Queue.xlsx")

RETURN_WINDOW_DAYS = 30
HYGIENE_CATEGORIES = {"underwear", "swimwear", "socks", "hosiery"}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [RPA] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a"),
        logging.StreamHandler()
    ]
)

COLS = {
    "Order_ID": 1, "Customer_Name": 2, "Item_Type": 3, "Purchase_Date": 4,
    "Return_Date": 5, "Hygiene_Flag": 6, "Final_Sale_Flag": 7, "Image_Path": 8,
    "RPA_Status": 9, "AI_Decision": 10, "AI_Defect": 11, "AI_Confidence": 12, "Notes": 13
}


def check_eligibility(order_id, item_type, purchase_date_str, hygiene_flag, final_sale_flag):
    today = datetime.today()

    if hygiene_flag.strip().lower() == "yes":
        return "REJECTED - Hygiene Item", f"Item type '{item_type}' is non-returnable (hygiene policy)"

    if final_sale_flag.strip().lower() == "yes":
        return "REJECTED - Final Sale", "Item marked as Final Sale; returns not accepted"

    if item_type.strip().lower() in HYGIENE_CATEGORIES:
        return "REJECTED - Hygiene Category", f"'{item_type}' falls under hygiene category policy"

    try:
        purchase_date = datetime.strptime(purchase_date_str.strip(), "%Y-%m-%d")
    except ValueError:
        return "REJECTED - Invalid Date", f"Cannot parse purchase date: {purchase_date_str}"

    days_since_purchase = (today - purchase_date).days

    if days_since_purchase > RETURN_WINDOW_DAYS:
        return (
            "REJECTED - Outside Window",
            f"Purchase was {days_since_purchase} days ago (limit: {RETURN_WINDOW_DAYS} days)"
        )

    return "ELIGIBLE FOR AI INSPECTION", f"Purchase was {days_since_purchase} days ago - within return window"


def run():
    logging.info("=" * 60)
    logging.info("RPA Eligibility Bot started")
    logging.info("=" * 60)

    wb = openpyxl.load_workbook(EXCEL_FILE)
    ws = wb.active

    eligible_count = 0
    rejected_count = 0

    for row in ws.iter_rows(min_row=2, values_only=False):
        order_id     = str(row[COLS["Order_ID"] - 1].value or "").strip()
        item_type    = str(row[COLS["Item_Type"] - 1].value or "").strip()
        purchase_date= str(row[COLS["Purchase_Date"] - 1].value or "").strip()
        hygiene_flag = str(row[COLS["Hygiene_Flag"] - 1].value or "No").strip()
        final_sale   = str(row[COLS["Final_Sale_Flag"] - 1].value or "No").strip()

        if not order_id:
            continue

        status, note = check_eligibility(order_id, item_type, purchase_date, hygiene_flag, final_sale)

        row[COLS["RPA_Status"] - 1].value = status
        row[COLS["Notes"] - 1].value = note

        if "ELIGIBLE" in status:
            eligible_count += 1
            logging.info(f"[{order_id}] {item_type} -> ELIGIBLE | {note}")
        else:
            rejected_count += 1
            logging.info(f"[{order_id}] {item_type} -> {status} | {note}")

    wb.save(EXCEL_FILE)
    logging.info("-" * 60)
    logging.info(f"RPA complete. Eligible: {eligible_count} | Rejected: {rejected_count}")
    logging.info("=" * 60)
    return eligible_count, rejected_count


if __name__ == "__main__":
    run()
