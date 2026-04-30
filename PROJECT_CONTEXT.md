# Project Context: Clothing Returns Automation
# H9IAPA: Intelligent Agents and Process Automation
# National College of Ireland - MSc Artificial Intelligence for Business

---

## What We Are Building

An automated clothing returns processing system for an e-commerce retailer. The system replaces a manual, human-driven returns inspection process with a two-stage Python pipeline:

**Stage 1 - RPA-style Eligibility Checker** (`rpa_eligibility.py`)
Mimics a Robotic Process Automation bot. Reads a structured Excel queue, applies deterministic business rules, and writes pass/fail decisions back to the file. No UI automation is used - this is rule-based scripted automation, which qualifies as RPA-style logic per the academic brief.

**Stage 2 - Agentic AI Inspector** (`agent_inspector.py`)
An intelligent agent that picks up eligible returns from Stage 1, encodes garment images as base64, and calls the Claude claude-sonnet-4-20250514 vision API to detect defects. The agent reasons autonomously and outputs a structured JSON decision. This is the agentic/AI-driven automation component.

**Stage 3 - Orchestrator** (`orchestrator.py`)
Runs Stage 1 then Stage 2 in sequence. Single entry point for the full demo.

---

## Academic Context

- **Module:** H9IAPA - Intelligent Agents and Process Automation
- **Assessment:** Individual CA worth 100% of module marks
- **Target grade:** H1 (>70%)
- **Submission deadline:** Thursday 30 April 2026 at 23:55
- **Deliverables:** PDF report (max 10 pages), working code implementation, 7-minute video with slides

The brief requires two distinct automation types applied to a business process:
1. RPA-based automation for rule-based, structured tasks
2. Agentic or AI-driven automation for cognitive, perception-based tasks

Both are implemented here in pure Python as permitted by the brief ("tool of your choice, e.g. Python, UiPath").

---

## Business Process

**Domain:** Retail E-commerce - Clothing

**Process:** Customer-initiated product return for clothing items.

**As-Is (manual) process:**
1. Customer submits return request with order details and photos
2. Staff member manually checks purchase date against 30-day policy
3. Staff member checks if item is a hygiene/final-sale category
4. Staff member visually inspects the garment photo for defects
5. Staff member logs decision in spreadsheet and emails customer

**To-Be (automated) process:**
1. Customer submits return request (order ID, purchase date, item type, photo)
2. RPA bot reads the queue Excel, applies eligibility rules, updates status
3. AI agent picks up eligible rows, inspects garment image, outputs defect decision
4. Results written back to Excel automatically; escalations flagged for human review

---

## Folder Structure

```
clothing_returns/
├── data/
│   ├── Returns_Queue.xlsx        # Input/output data file with 10 sample returns
│   └── images/                   # 10 synthetic garment images
│       ├── jacket_damaged.jpg
│       ├── jeans_clean.jpg
│       ├── tshirt_stain.jpg
│       ├── underwear.jpg
│       ├── dress_tear.jpg
│       ├── hoodie_clean.jpg
│       ├── coat_pilling.jpg
│       ├── trousers_clean.jpg
│       ├── swimwear.jpg
│       └── blazer_missing_button.jpg
├── rpa_eligibility.py            # Stage 1: RPA eligibility checker
├── agent_inspector.py            # Stage 2: Claude vision AI inspector
├── orchestrator.py               # Stage 3: Pipeline runner
├── returns_log.txt               # Auto-generated run log
└── docs/
    ├── PROJECT_CONTEXT.md        # This file
    └── CLAUDE_CODE_PROMPTS.md    # Step-by-step prompts for building/running
```

---

## Data File: Returns_Queue.xlsx

The Excel file is the shared data layer between both scripts. It has 13 columns:

| Column | Description |
|--------|-------------|
| Order_ID | Unique return reference (e.g. ORD-1001) |
| Customer_Name | Customer full name |
| Item_Type | Clothing category (Jacket, Jeans, Dress, etc.) |
| Purchase_Date | Date item was originally bought (YYYY-MM-DD) |
| Return_Date | Date return was requested |
| Hygiene_Flag | "Yes" if item is a hygiene product (underwear, swimwear) |
| Final_Sale_Flag | "Yes" if item was sold as non-returnable |
| Image_Path | Relative path to garment image (e.g. images/jacket_damaged.jpg) |
| RPA_Status | Written by Stage 1 - eligibility decision |
| AI_Decision | Written by Stage 2 - AUTO_APPROVE / REJECT / ESCALATE |
| AI_Defect | Written by Stage 2 - defect class detected |
| AI_Confidence | Written by Stage 2 - model confidence score (0.0 to 1.0) |
| Notes | Human-readable reasoning from whichever stage last processed the row |

---

## Business Rules

### Stage 1 - RPA Rules (deterministic, applied in order)

| Condition | Output Status |
|-----------|--------------|
| Hygiene_Flag = "Yes" | REJECTED - Hygiene Item |
| Final_Sale_Flag = "Yes" | REJECTED - Final Sale |
| Item type in {underwear, swimwear, socks, hosiery} | REJECTED - Hygiene Category |
| Days since Purchase_Date > 30 | REJECTED - Outside Window |
| All checks pass | ELIGIBLE FOR AI INSPECTION |

### Stage 2 - AI Agent Rules (applied to eligible rows only)

| Condition | Decision |
|-----------|----------|
| Confidence >= 0.85 AND defect = no_defect | AUTO_APPROVE |
| Any defect detected | REJECT |
| Confidence between 0.50 and 0.84 | ESCALATE |

### Defect Classes the AI Agent Detects
- `stain` - food, liquid, or ink marks
- `tear` - rips, holes, or fabric damage
- `pilling` - surface bobbling or fuzzing
- `missing_button` - absent or broken buttons, zips, or fasteners
- `no_defect` - item appears in good condition

---

## Sample Data Overview

10 rows pre-loaded in Returns_Queue.xlsx covering every scenario:

| Order | Item | Scenario | Expected RPA | Expected AI |
|-------|------|----------|-------------|-------------|
| ORD-1001 | Jacket | Recent, damaged | ELIGIBLE | REJECT (tear) |
| ORD-1002 | Jeans | Recent, clean | ELIGIBLE | AUTO_APPROVE |
| ORD-1003 | T-Shirt | 45 days old | REJECTED - Outside Window | - |
| ORD-1004 | Underwear | Hygiene flag | REJECTED - Hygiene Item | - |
| ORD-1005 | Dress | Recent, torn | ELIGIBLE | REJECT (tear) |
| ORD-1006 | Hoodie | Final sale | REJECTED - Final Sale | - |
| ORD-1007 | Winter Coat | Recent, pilling | ELIGIBLE | REJECT (pilling) |
| ORD-1008 | Trousers | Recent, clean | ELIGIBLE | AUTO_APPROVE |
| ORD-1009 | Swimwear | Hygiene flag | REJECTED - Hygiene Item | - |
| ORD-1010 | Blazer | Recent, missing button | ELIGIBLE | REJECT (missing button) |

---

## Key Technical Decisions

**Why pure Python instead of UiPath + Python?**
The CA brief says "tool of your choice (e.g., Python, UiPath)". UiPath would require installation, licensing, and a working Windows Studio environment - too risky for a same-day submission. Pure Python is faster to build, easier to demo, and fully satisfies the brief. The RPA script reads/writes Excel and applies structured business rules, which is the essence of RPA logic regardless of the tool.

**Why Claude vision instead of YOLOv8?**
Training a custom YOLOv8 model on clothing defects requires a labelled dataset and compute time not available in a single day. Claude's vision API provides zero-shot defect detection with structured JSON output, which is more accurately described as "agentic AI" anyway - it reasons about the image rather than just classifying pixels.

**Why synthetic images?**
Sourcing real product photos with confirmed defect labels raises copyright and data quality issues. Programmatically generated images with known defect types provide a clean, reproducible demo dataset where we know exactly what the AI should find.

---

## Environment Setup

**Dependencies:**
```bash
pip install openpyxl anthropic pillow
```

**API key:**
```bash
export ANTHROPIC_API_KEY=your_key_here
```

**Run full pipeline:**
```bash
cd clothing_returns
python orchestrator.py
```

---

## What Claude Code Should Know

When working on this project:

1. The Excel file is the shared state between scripts. Always load it fresh at the start of each script run.
2. Image paths in the Excel are relative (e.g. `images/jacket_damaged.jpg`). The base directory is the `data/` folder. Full path = `data/` + image_path value.
3. Stage 2 only processes rows where `RPA_Status` is exactly `"ELIGIBLE FOR AI INSPECTION"`. All other rows are skipped.
4. The Claude API call in `agent_inspector.py` must return valid JSON. The script has a fallback JSON parse that strips markdown fences if Claude wraps the output.
5. All decisions are written back to `Returns_Queue.xlsx` in-place using openpyxl. Do not use pandas to write back as it strips formatting.
6. `returns_log.txt` is appended on each run, not overwritten. This preserves the audit trail across multiple runs.
