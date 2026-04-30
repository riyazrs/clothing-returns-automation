"""
Script 2: Agentic AI Garment Inspector
H9IAPA - Clothing Returns Automation
Uses Claude claude-sonnet-4-20250514 vision to inspect garment images and make return decisions.
Agentic behaviour: autonomous multi-step reasoning -> structured decision output.
"""

import anthropic
import openpyxl
import base64
import json
import logging
import os
from pathlib import Path

LOG_FILE = os.path.join(os.path.dirname(__file__), "returns_log.txt")
EXCEL_FILE = os.path.join(os.path.dirname(__file__), "data", "Returns_Queue.xlsx")
IMAGES_DIR = os.path.join(os.path.dirname(__file__), "data")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [AGENT] %(message)s",
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

SYSTEM_PROMPT = """You are an expert garment quality inspector for an e-commerce clothing returns system.

Your job is to analyse a clothing item image and detect any defects.

Defect categories to look for:
- stain: visible marks, discolouration, food/liquid stains
- tear: rips, holes, or fabric damage
- pilling: fabric bobbling or fuzzing on surface
- missing_button: absent or broken button/zip/fastener
- no_defect: item appears to be in good condition

Decision rules (apply strictly):
- If confidence >= 0.85 AND defect = no_defect -> AUTO_APPROVE
- If any defect detected -> REJECT
- If confidence is between 0.50 and 0.84 (uncertain) -> ESCALATE

Respond ONLY with a valid JSON object in this exact format (no markdown, no explanation):
{
  "defect_detected": "stain" | "tear" | "pilling" | "missing_button" | "no_defect",
  "confidence": 0.00,
  "decision": "AUTO_APPROVE" | "REJECT" | "ESCALATE",
  "reasoning": "one sentence explanation"
}"""


def encode_image(image_path: str) -> tuple[str, str]:
    ext = Path(image_path).suffix.lower()
    media_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}
    media_type = media_map.get(ext, "image/jpeg")
    with open(image_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8"), media_type


def inspect_garment(client: anthropic.Anthropic, order_id: str, item_type: str, image_path: str) -> dict:
    full_path = os.path.join(IMAGES_DIR, image_path)

    if not os.path.exists(full_path):
        logging.warning(f"[{order_id}] Image not found: {full_path}")
        return {
            "defect_detected": "unknown",
            "confidence": 0.0,
            "decision": "ESCALATE",
            "reasoning": "Image file not found - manual review required"
        }

    image_data, media_type = encode_image(full_path)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data
                        }
                    },
                    {
                        "type": "text",
                        "text": f"Inspect this {item_type} for defects and return your JSON decision."
                    }
                ]
            }
        ]
    )

    raw = message.content[0].text.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        clean = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean)

    return result


def run():
    logging.info("=" * 60)
    logging.info("AI Garment Inspector Agent started")
    logging.info("=" * 60)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY environment variable not set")

    client = anthropic.Anthropic(api_key=api_key)

    wb = openpyxl.load_workbook(EXCEL_FILE)
    ws = wb.active

    approved = rejected = escalated = skipped = 0

    for row in ws.iter_rows(min_row=2, values_only=False):
        order_id   = str(row[COLS["Order_ID"] - 1].value or "").strip()
        item_type  = str(row[COLS["Item_Type"] - 1].value or "").strip()
        image_path = str(row[COLS["Image_Path"] - 1].value or "").strip()
        rpa_status = str(row[COLS["RPA_Status"] - 1].value or "").strip()

        if not order_id:
            continue

        if "ELIGIBLE FOR AI INSPECTION" not in rpa_status:
            logging.info(f"[{order_id}] Skipping - RPA status: {rpa_status}")
            skipped += 1
            continue

        logging.info(f"[{order_id}] Inspecting {item_type} | image: {image_path}")

        result = inspect_garment(client, order_id, item_type, image_path)

        row[COLS["AI_Decision"] - 1].value    = result.get("decision", "ESCALATE")
        row[COLS["AI_Defect"] - 1].value      = result.get("defect_detected", "unknown")
        row[COLS["AI_Confidence"] - 1].value  = result.get("confidence", 0.0)
        row[COLS["Notes"] - 1].value          = result.get("reasoning", "")

        decision = result.get("decision", "ESCALATE")
        if decision == "AUTO_APPROVE":
            approved += 1
        elif decision == "REJECT":
            rejected += 1
        else:
            escalated += 1

        logging.info(
            f"[{order_id}] -> {decision} | defect={result.get('defect_detected')} "
            f"confidence={result.get('confidence')} | {result.get('reasoning')}"
        )

    wb.save(EXCEL_FILE)
    logging.info("-" * 60)
    logging.info(f"Agent complete. Approved: {approved} | Rejected: {rejected} | Escalated: {escalated} | Skipped: {skipped}")
    logging.info("=" * 60)
    return approved, rejected, escalated


if __name__ == "__main__":
    run()
