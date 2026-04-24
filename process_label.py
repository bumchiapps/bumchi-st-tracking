import os
import csv
from datetime import datetime
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import Optional

# 1. Schema Definition
class ShippingDetails(BaseModel):
    order_id: Optional[str]
    name: Optional[str]
    phone: Optional[str]
    tracking_id: Optional[str]

# Setup Gemini Client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def log_to_csv(details: ShippingDetails, filename: str):
    csv_file = "shipping_master_log.csv"
    file_exists = os.path.isfile(csv_file)
    
    with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Source File", "Order ID", "Name", "Phone", "Tracking ID"])
        
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            filename,
            details.order_id, 
            details.name, 
            details.phone, 
            details.tracking_id
        ])

def process_label(image_path):
    filename = os.path.basename(image_path)
    ext = filename.lower().split('.')[-1]
    
    with open(image_path, "rb") as f:
        image_bytes = f.read()
        
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[
                "Extract Order ID, Name, and Phone. Also find the ST Courier tracking number from the barcode.",
                types.Part.from_bytes(data=image_bytes, mime_type=f"image/{ext if ext != 'jpg' else 'jpeg'}")
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ShippingDetails,
                temperature=0.1,
            )
        )
        
        details: ShippingDetails = response.parsed
        log_to_csv(details, filename)
        return True
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return False

if __name__ == "__main__":
    target_dir = "labels/pending"
    
    if not os.path.exists(target_dir):
        print("No pending directory found.")
        exit(0)

    files = [f for f in os.listdir(target_dir) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
    
    if not files:
        print("No labels to process.")
        exit(0)

    for filename in files:
        full_path = os.path.join(target_dir, filename)
        if process_label(full_path):
            os.remove(full_path) # Delete image after logging
            print(f"Processed and deleted: {filename}")
