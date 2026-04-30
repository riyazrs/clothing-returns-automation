# H9IAPA - Clothing Returns Automation
# Claude Code Master Prompt Document
# Use these prompts sequentially in Claude Code (claude code CLI)

---

## PROJECT CONTEXT

You are building a two-part automation system for a clothing e-commerce returns process.

**Domain:** Retail / E-commerce (Clothing)
**Process:** Automated Clothing Returns & Quality Assurance
**Stack:** Python only (no UiPath)
**Two automation types:**
1. RPA-style: Rule-based eligibility checker (reads/writes Excel)
2. Agentic AI: Claude vision-based garment defect inspector

**Folder structure:**
```
clothing_returns/
├── data/
│   ├── Returns_Queue.xlsx       # Input/output data file
│   └── images/                  # Garment images (10 synthetic images)
├── rpa_eligibility.py           # Script 1 - RPA logic
├── agent_inspector.py           # Script 2 - Agentic AI logic
├── orchestrator.py              # Script 3 - Pipeline runner
├── returns_log.txt              # Auto-generated log
└── docs/
    └── CLAUDE_CODE_PROMPTS.md   # This file
```

---

## PROMPT 1 — ENVIRONMENT SETUP

Use this first to confirm dependencies and structure are correct.

```
Check the clothing_returns project folder:
1. Confirm these files exist: rpa_eligibility.py, agent_inspector.py, orchestrator.py, data/Returns_Queue.xlsx
2. Confirm the data/images/ folder has 10 .jpg files
3. Install any missing Python dependencies: openpyxl, anthropic, pillow
4. Print a summary of what exists and what is missing
```

---

## PROMPT 2 — RUN THE RPA SCRIPT

```
Run rpa_eligibility.py in the clothing_returns directory.

The script should:
- Read data/Returns_Queue.xlsx
- Apply these business rules to each row:
  * If Hygiene_Flag = "Yes" -> REJECTED - Hygiene Item
  * If Final_Sale_Flag = "Yes" -> REJECTED - Final Sale
  * If days since Purchase_Date > 30 -> REJECTED - Outside Window
  * Otherwise -> ELIGIBLE FOR AI INSPECTION
- Write the RPA_Status and Notes columns back to the Excel file
- Log all decisions to returns_log.txt

After running, show me:
1. The console output
2. A summary table of Order_ID vs RPA_Status
```

---

## PROMPT 3 — RUN THE AGENTIC AI INSPECTOR

```
Run agent_inspector.py in the clothing_returns directory.

Before running, set the ANTHROPIC_API_KEY environment variable to my key.

The script should:
- Read only rows where RPA_Status = "ELIGIBLE FOR AI INSPECTION"
- For each eligible row, encode the garment image from data/images/ as base64
- Send the image to Claude claude-sonnet-4-20250514 vision API with the garment inspector system prompt
- Parse the JSON response containing: defect_detected, confidence, decision, reasoning
- Apply decision rules:
  * confidence >= 0.85 AND no_defect -> AUTO_APPROVE
  * any defect detected -> REJECT
  * confidence 0.50-0.84 -> ESCALATE
- Write AI_Decision, AI_Defect, AI_Confidence, Notes back to Excel

After running, show me a summary table: Order_ID | Item_Type | AI_Decision | AI_Defect | AI_Confidence
```

---

## PROMPT 4 — RUN THE FULL PIPELINE

```
Run the complete returns pipeline using orchestrator.py.

Steps:
1. Make sure ANTHROPIC_API_KEY is exported
2. Run: python orchestrator.py from the clothing_returns directory
3. The orchestrator runs Stage 1 (RPA) then Stage 2 (AI) in sequence
4. Show me the full console log output
5. After completion, read Returns_Queue.xlsx and print all rows with their final statuses as a formatted table
```

---

## PROMPT 5 — DEBUG: IMAGE NOT FOUND ERRORS

If you see "Image not found" errors, use this:

```
The agent_inspector.py is failing to find images.

Investigate:
1. Print the exact image_path value from each Excel row
2. Print the IMAGES_DIR variable value in agent_inspector.py
3. List all files in data/images/
4. Fix the path resolution so image_path in Excel joins correctly with IMAGES_DIR

The image paths in Excel are stored as "images/jacket_damaged.jpg" etc.
IMAGES_DIR should be the "data" folder, so the full path = IMAGES_DIR + "/" + image_path
```

---

## PROMPT 6 — ADD A NEW TEST CASE

```
Add a new row to data/Returns_Queue.xlsx with these values:
- Order_ID: ORD-1011
- Customer_Name: Test User
- Item_Type: Cardigan
- Purchase_Date: [7 days ago from today]
- Return_Date: [today]
- Hygiene_Flag: No
- Final_Sale_Flag: No
- Image_Path: images/trousers_clean.jpg   (reuse existing image for test)
- All other columns: empty

Then re-run the full pipeline (orchestrator.py) and show the result for ORD-1011 only.
```

---

## PROMPT 7 — GENERATE RESULTS REPORT

```
After running the full pipeline, generate a results summary:

1. Read Returns_Queue.xlsx
2. Print a formatted console report with:
   - Total returns processed
   - Breakdown: RPA rejected (with reasons) vs AI inspected
   - Of AI inspected: AUTO_APPROVE / REJECT / ESCALATE counts
   - List of escalated orders for human review
3. Also read returns_log.txt and show the last 30 lines
```

---

## PROMPT 8 — VERIFY EXCEL OUTPUT

```
Open data/Returns_Queue.xlsx and verify:
1. All 10 rows have a value in RPA_Status column
2. Rows marked ELIGIBLE FOR AI INSPECTION also have values in AI_Decision, AI_Defect, AI_Confidence
3. RPA-rejected rows have empty AI columns (they were never sent to the agent)
4. Print any rows where data looks incorrect or missing

If any data is missing or incorrect, re-run the relevant script to fix it.
```

---

## BUSINESS RULES REFERENCE

### RPA Rules (rpa_eligibility.py)
| Condition | Status |
|-----------|--------|
| Hygiene_Flag = "Yes" | REJECTED - Hygiene Item |
| Final_Sale_Flag = "Yes" | REJECTED - Final Sale |
| Item type in {underwear, swimwear, socks} | REJECTED - Hygiene Category |
| Days since purchase > 30 | REJECTED - Outside Window |
| All checks pass | ELIGIBLE FOR AI INSPECTION |

### AI Agent Rules (agent_inspector.py)
| Condition | Decision |
|-----------|----------|
| confidence >= 0.85 AND defect = no_defect | AUTO_APPROVE |
| Any defect detected | REJECT |
| confidence 0.50 - 0.84 | ESCALATE |

---

## EXPECTED OUTCOMES FOR SAMPLE DATA

| Order | Item | Expected RPA | Expected AI |
|-------|------|-------------|-------------|
| ORD-1001 | Jacket | ELIGIBLE | REJECT (tear) |
| ORD-1002 | Jeans | ELIGIBLE | AUTO_APPROVE |
| ORD-1003 | T-Shirt | REJECTED - Outside Window | - |
| ORD-1004 | Underwear | REJECTED - Hygiene Item | - |
| ORD-1005 | Dress | ELIGIBLE | REJECT (tear) |
| ORD-1006 | Hoodie | REJECTED - Final Sale | - |
| ORD-1007 | Winter Coat | ELIGIBLE | REJECT (pilling) |
| ORD-1008 | Trousers | ELIGIBLE | AUTO_APPROVE |
| ORD-1009 | Swimwear | REJECTED - Hygiene Item | - |
| ORD-1010 | Blazer | ELIGIBLE | REJECT (missing button) |

---

## TROUBLESHOOTING

**API key error:**
```bash
export ANTHROPIC_API_KEY=your_key_here
python orchestrator.py
```

**Module not found:**
```bash
pip install openpyxl anthropic pillow --break-system-packages
```

**Excel file locked:**
Close the file in any spreadsheet app before running scripts.

**JSON parse error from Claude:**
The agent_inspector.py handles this with a fallback strip. If it still fails, check the raw API response and add the order_id to the log for manual review.
