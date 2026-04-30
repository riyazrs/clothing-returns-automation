import os
import json
import time
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler

REPO_OWNER = "riyazrs"
REPO_NAME = "clothing-returns-automation"


def gh_request(method, url, token, body=None):
    """Make a GitHub API request using only stdlib urllib."""
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
            "User-Agent": "clothing-returns-vercel"
        }
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
        except Exception as e:
            self._respond(400, {"error": f"Invalid request body: {e}"})
            return

        token = os.environ.get("GH_TOKEN")
        if not token:
            self._respond(500, {"error": "GH_TOKEN environment variable not set"})
            return

        try:
            customer     = data.get("customer_name", "").strip()
            item_type    = data.get("item_type", "").strip()
            purchase_date = data.get("purchase_date", "").strip()
            hygiene      = data.get("hygiene_item", "No")
            final_sale   = data.get("final_sale", "No")
            image_base64 = data.get("image_base64", "")
            image_name   = data.get("image_name", "upload.jpg")

            if not all([customer, item_type, purchase_date, image_base64]):
                self._respond(400, {"error": "Missing required fields: customer_name, item_type, purchase_date, image"})
                return

            # Build image filename
            ts = int(time.time())
            ext = image_name.rsplit('.', 1)[-1] if '.' in image_name else 'jpg'
            safe = "".join(c if c.isalnum() else '_' for c in item_type.lower())
            image_filename = f"{safe}_{ts}.{ext}"

            # Upload image to GitHub
            upload_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/data/submissions/{image_filename}"
            status, body = gh_request("PUT", upload_url, token, {
                "message": f"Upload garment image: {image_filename}",
                "content": image_base64
            })
            if status not in (200, 201):
                self._respond(status, {"error": f"GitHub upload failed: {body}"})
                return

            # Trigger workflow dispatch
            dispatch_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/pipeline.yml/dispatches"
            status, body = gh_request("POST", dispatch_url, token, {
                "ref": "main",
                "inputs": {
                    "mode": "single",
                    "customer_name": customer,
                    "item_type": item_type,
                    "purchase_date": purchase_date,
                    "hygiene_item": hygiene,
                    "final_sale": final_sale,
                    "image_filename": image_filename
                }
            })
            if status != 204:
                self._respond(status, {"error": f"Workflow trigger failed: {body}"})
                return

            self._respond(200, {
                "status": "success",
                "message": "Pipeline triggered",
                "image_filename": image_filename
            })

        except Exception as e:
            self._respond(500, {"error": str(e)})

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def _respond(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self._cors()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
