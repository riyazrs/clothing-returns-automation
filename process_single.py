"""
Process a single return submission from GitHub Actions workflow inputs.
Runs the item through RPA eligibility check, then AI inspection if eligible.
Appends the result to Returns_Queue.xlsx and writes a standalone result JSON.
"""
import os
import sys
import json
import logging
import openpyxl
from datetime import datetime
from pathlib import Path

LOG_FILE = os.path.join(os.path.dirname(__file__), "returns_log.txt")
EXCEL_FILE = os.path.join(os.path.dirname(__file__), "data", "Returns_Queue.xlsx")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SINGLE] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a"),
        logging.StreamHandler()
    ]
)


def main():
    customer = os.environ.get("SUBMIT_CUSTOMER", "").strip()
    item_type = os.environ.get("SUBMIT_ITEM_TYPE", "").strip()
    purchase_date = os.environ.get("SUBMIT_PURCHASE_DATE", "").strip()
    hygiene = os.environ.get("SUBMIT_HYGIENE", "No").strip()
    final_sale = os.environ.get("SUBMIT_FINAL_SALE", "No").strip()
    image_filename = os.environ.get("SUBMIT_IMAGE", "").strip()

    if not customer or not item_type or not purchase_date:
        logging.error("Missing required fields: customer_name, item_type, purchase_date")
        sys.exit(1)

    # Generate order ID based on existing rows
    wb = openpyxl.load_workbook(EXCEL_FILE)
    ws = wb.active
    max_row = ws.max_row
    order_num = 1001 + max_row - 1  # header is row 1
    order_id = f"ORD-{order_num}"

    # Determine image path
    if image_filename:
        image_path = f"submissions/{image_filename}"
        full_image = os.path.join(os.path.dirname(__file__), "data", image_path)
        if not os.path.exists(full_image):
            logging.warning(f"Submitted image not found: {full_image}")
    else:
        image_path = ""

    logging.info("=" * 60)
    logging.info(f"SINGLE SUBMISSION: {order_id}")
    logging.info(f"  Customer: {customer}")
    logging.info(f"  Item: {item_type}")
    logging.info(f"  Purchase Date: {purchase_date}")
    logging.info(f"  Hygiene: {hygiene}, Final Sale: {final_sale}")
    logging.info(f"  Image: {image_path or 'none'}")
    logging.info("=" * 60)

    # Stage 1: RPA eligibility check
    from rpa_eligibility import check_eligibility
    rpa_status, rpa_note = check_eligibility(order_id, item_type, purchase_date, hygiene, final_sale)
    logging.info(f"RPA Result: {rpa_status} | {rpa_note}")

    # Write intermediate RPA status so frontend can show phase-aware message
    docs_dir = os.path.join(os.path.dirname(__file__), "docs")
    os.makedirs(docs_dir, exist_ok=True)
    with open(os.path.join(docs_dir, "rpa_status.json"), "w") as f:
        json.dump({
            "order_id": order_id,
            "rpa_status": rpa_status,
            "rpa_note": rpa_note,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }, f)

    ai_decision = None
    ai_defect = None
    ai_confidence = None
    ai_note = rpa_note

    # Stage 2: AI inspection if eligible
    if "ELIGIBLE" in rpa_status and image_path:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            logging.error("ANTHROPIC_API_KEY not set, cannot run AI inspection")
            ai_decision = "ESCALATE"
            ai_note = "API key missing - manual review required"
        else:
            import anthropic
            from agent_inspector import inspect_garment
            client = anthropic.Anthropic(api_key=api_key)
            result = inspect_garment(client, order_id, item_type, image_path)
            ai_decision = result.get("decision", "ESCALATE")
            ai_defect = result.get("defect_detected", "unknown")
            ai_confidence = result.get("confidence", 0.0)
            ai_note = result.get("reasoning", "")
            logging.info(f"AI Result: {ai_decision} | defect={ai_defect} conf={ai_confidence}")
    elif "ELIGIBLE" in rpa_status and not image_path:
        ai_decision = "ESCALATE"
        ai_note = "No image provided - manual review required"
        logging.info("No image provided, escalating to manual review")

    # Append row to Excel
    return_date = datetime.today().strftime("%Y-%m-%d")
    new_row = [
        order_id, customer, item_type, purchase_date, return_date,
        hygiene, final_sale, image_path,
        rpa_status, ai_decision, ai_defect, ai_confidence, ai_note
    ]
    ws.append(new_row)
    wb.save(EXCEL_FILE)
    logging.info(f"Result appended to {EXCEL_FILE}")

    # Write standalone result for the frontend to fetch
    single_result = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "order_id": order_id,
        "customer_name": customer,
        "item_type": item_type,
        "purchase_date": purchase_date,
        "rpa_status": rpa_status,
        "rpa_note": rpa_note,
        "ai_decision": ai_decision,
        "ai_defect": ai_defect,
        "ai_confidence": ai_confidence,
        "ai_reasoning": ai_note,
        "image_path": image_path
    }
    result_path = os.path.join(os.path.dirname(__file__), "docs", "latest_submission.json")
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, "w") as f:
        json.dump(single_result, f, indent=2, default=str)
    logging.info(f"Single result written to {result_path}")
    logging.info("=" * 60)


if __name__ == "__main__":
    main()
