import os
import json
import base64
import time
import requests
from http.server import BaseHTTPRequestHandler

# Configuration - You will set these as Environment Variables in Vercel
REPO_OWNER = "riyazrs"
REPO_NAME = "clothing-returns-automation"

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        token = os.environ.get("GH_TOKEN")
        if not token:
            self._respond(500, {"error": "Server configuration error: GH_TOKEN missing"})
            return

        try:
            # 1. Extract data
            customer = data.get("customer_name")
            item_type = data.get("item_type")
            purchase_date = data.get("purchase_date")
            hygiene = data.get("hygiene_item", "No")
            final_sale = data.get("final_sale", "No")
            image_base64 = data.get("image_base64")
            image_name = data.get("image_name")

            if not all([customer, item_type, purchase_date, image_base64]):
                self._respond(400, {"error": "Missing required fields"})
                return

            # 2. Upload image to GitHub
            ts = int(time.time())
            ext = image_name.split('.')[-1] if '.' in image_name else 'jpg'
            safe_item = "".join([c for c in item_type.lower() if c.isalnum() or c == ' ']).replace(' ', '_')
            image_filename = f"{safe_item}_{ts}.{ext}"
            
            upload_path = f"data/submissions/{image_filename}"
            upload_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{upload_path}"
            
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            upload_body = {
                "message": f"Upload garment image: {image_filename} (via Vercel)",
                "content": image_base64
            }
            
            up_resp = requests.put(upload_url, headers=headers, json=upload_body)
            if up_resp.status_code not in [200, 201]:
                self._respond(up_resp.status_code, {"error": f"GitHub Upload Failed: {up_resp.text}"})
                return

            # 3. Trigger Workflow Dispatch
            dispatch_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/pipeline.yml/dispatches"
            dispatch_body = {
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
            }
            
            dis_resp = requests.post(dispatch_url, headers=headers, json=dispatch_body)
            if dis_resp.status_code != 204:
                self._respond(dis_resp.status_code, {"error": f"Workflow Trigger Failed: {dis_resp.text}"})
                return

            self._respond(200, {
                "status": "success",
                "message": "Pipeline triggered successfully",
                "image_filename": image_filename
            })

        except Exception as e:
            self._respond(500, {"error": str(e)})

    def _respond(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
