import os
import google.generativeai as genai
import sys

# Setup Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def process_image(image_path):
    # Upload the file to the API
    sample_file = genai.upload_file(path=image_path, display_name="Shipping Label")

    # Ask Gemini to find the ID specifically
    prompt = "Read this shipping label. Extract only the Order ID number. Return just the number."
    response = model.generate_content([prompt, sample_file])
    
    order_id = response.text.strip()
    print(f"Detected Order ID: {order_id}")

    # --- ACTION LOGIC ---
    # Here is where you'd add: 
    # requests.post("https://your-api.com/send-tracking", data={"id": order_id})
    # --------------------

if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_image(sys.argv[1])
