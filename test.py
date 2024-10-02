import streamlit as st
import requests
import json
from time import sleep
from PIL import Image
import io
import base64
import os
from dotenv import load_dotenv
load_dotenv()
from caption import caption_img
from vton import virtual_tryon

def upload_image_to_imgbb(image, api_key):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": api_key,
        "image": img_str,
    }
    res = requests.post(url, payload)
    if res.ok:
        return res.json()['data']['url']
    else:
        st.error("Failed to upload image")
        return None

def main():
    st.title("Moose AI")
    
    # Initialize session state
    if 'start_generation' not in st.session_state:
        st.session_state.start_generation = False

    imgbb_api_key = os.getenv("IMGBB_API_KEY")
    
    col1, col2 = st.columns(2)
    
    with col1:
        model_file = st.file_uploader("Upload model image", type=["jpg", "png", "jpeg"])
        if model_file:
            model_img = Image.open(model_file)
            st.image(model_img, caption='Model Image', use_column_width=True)

    with col2:
        garment_file = st.file_uploader("Upload garment image", type=["jpg", "png", "jpeg"])
        if garment_file:
            garment_img = Image.open(garment_file)
            st.image(garment_img, caption='Garment Image', use_column_width=True)
    
    start_button = st.button("Generate")

    if start_button:
        st.session_state.start_generation = True

    if imgbb_api_key and model_file and garment_file and st.session_state.start_generation:
        with st.spinner('Processing'):
            model_url = upload_image_to_imgbb(model_img, imgbb_api_key)
            garment_url = upload_image_to_imgbb(garment_img, imgbb_api_key)

            download_garment = requests.get(garment_url)
            garment_img = Image.open(io.BytesIO(download_garment.content))
            garment_img.save("garment.png")
            garment_desc = caption_img("garment.png")[0]["generated_text"]
            os.remove("garment.png")

            result_url = virtual_tryon(model_url, garment_url, garment_desc)
            
        if result_url:
            st.image(result_url, caption='Virtual Try-on Result', use_column_width=True)
            
            response = requests.get(result_url)
            if response.status_code == 200:
                st.download_button(
                    label="Download Result Image",
                    data=response.content,
                    file_name="virtual_tryon_result.png",
                    mime="image/png"
                )
            else:
                st.error("Failed to prepare download for the result image.")

if __name__ == "__main__":
    main()