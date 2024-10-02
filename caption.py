import requests
import os
from dotenv import load_dotenv
load_dotenv()

API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
headers = {"Authorization": "Bearer " + os.getenv("HF_API_KEY")}

def caption_img(image_data):
    response = requests.post(API_URL, headers=headers, data=image_data)
    return response.json()