import requests
import json
from time import sleep
from caption import caption_img
import os
from dotenv import load_dotenv
load_dotenv()

URL = os.getenv("API_ENDPOINT")

def virtual_tryon(model_img, garment_img, garment_desc):
    payload = json.dumps({
        "key": os.getenv("API_KEY"),
        "prompt": "A realistic photo of a model wearing " + garment_desc,
        "negative_prompt": "Low quality, unrealistic, bad cloth, warped cloth, badly-fitted, arms outside sleeves",
        "init_image": model_img,
        "cloth_image": garment_img,
        "cloth_type": "upper_body",
        "height": 512,
        "width": 384,
        "guidance_scale": 8.0,
        "num_inference_steps": 20,
        "seed": 128915590,
        "temp": "no",
        "webhook": None,
        "track_id": None 
    })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", URL, headers=headers, data=payload)
    response = response.json()
    print(response)
    eta, fetch_result = response["eta"], response["fetch_result"]
    fetch_result = fetch_result.replace(r"\/", "/")

    sleep(eta*10)
    response = requests.request("POST", fetch_result, headers=headers, data=payload)
    response = response.json()
    print(response)
    result_url = response["output"][0].replace(r"\/", "/")
    
    return result_url