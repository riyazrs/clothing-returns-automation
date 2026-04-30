"""
Script 3: Orchestrator
H9IAPA - Clothing Returns Automation
Runs the full pipeline: RPA eligibility check -> AI garment inspection.
Single entry point for demo.
"""

import os
import sys
import logging
from datetime import datetime

LOG_FILE = os.path.join(os.path.dirname(__file__), "returns_log.txt")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ORCHESTRATOR] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a"),
        logging.StreamHandler()
    ]
)


def main():
    logging.info("=" * 60)
    logging.info(f"CLOTHING RETURNS PIPELINE STARTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("=" * 60)

    # Check API key upfront
    if not os.environ.get("ANTHROPIC_API_KEY"):
        logging.error("ANTHROPIC_API_KEY not set. Export it before running.")
        logging.error("  export ANTHROPIC_API_KEY=your_key_here")
        sys.exit(1)

    # Stage 1: RPA Eligibility
    logging.info("STAGE 1: Running RPA Eligibility Checker...")
    from rpa_eligibility import run as rpa_run
    eligible, rejected_rpa = rpa_run()
    logging.info(f"STAGE 1 COMPLETE -> {eligible} eligible, {rejected_rpa} rejected by RPA")

    # Stage 2: AI Inspection
    if eligible > 0:
        logging.info("STAGE 2: Running AI Garment Inspector...")
        from agent_inspector import run as agent_run
        approved, rejected_ai, escalated = agent_run()
        logging.info(f"STAGE 2 COMPLETE -> {approved} approved, {rejected_ai} rejected, {escalated} escalated")
    else:
        logging.info("STAGE 2: Skipped - no eligible items found")
        approved = rejected_ai = escalated = 0

    # Summary
    logging.info("=" * 60)
    logging.info("PIPELINE SUMMARY")
    logging.info(f"  Total processed     : {eligible + rejected_rpa}")
    logging.info(f"  RPA rejected        : {rejected_rpa}")
    logging.info(f"  AI approved         : {approved}")
    logging.info(f"  AI rejected         : {rejected_ai}")
    logging.info(f"  Escalated to human  : {escalated}")
    logging.info(f"  Results saved to    : data/Returns_Queue.xlsx")
    logging.info(f"  Full log at         : returns_log.txt")
    logging.info("=" * 60)


if __name__ == "__main__":
    main()
