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

logging.basicConfig(level=logging.INFO)

def upload_image_to_imgbb(image, api_key):
    # buffered = io.BytesIO()
    # image.save(buffered, format="PNG")
    # img_str = base64.b64encode(buffered.getvalue()).decode()
    # url = "https://api.imgbb.com/1/upload"
    # payload = {
    #     "key": api_key,
    #     "image": img_str,
    # }
    # res = requests.post(url, payload)
    # if res.ok:
    #     return res.json()['data']['url']
    # else:
    #     st.error("Failed to upload image")
    #     return None
    
    try:
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": api_key,
            "image": img_str,
        }
        res = requests.post(url, payload)
        res.raise_for_status()
        return res.json()['data']['url']
    except Exception as e:
        logging.error(f"Failed to upload image: {str(e)}")
        st.error(f"Failed to upload image: {str(e)}")
        return None

def main():
    st.title("Moose AI")
    
    # Initialize session state
    if 'start_generation' not in st.session_state:
        st.session_state.start_generation = False

    imgbb_api_key = os.getenv("IMGBB_API_KEY")
    
    model_file = st.file_uploader("Upload model image", type=["jpg", "png", "jpeg"])
    garment_file = st.file_uploader("Upload garment image", type=["jpg", "png", "jpeg"])
    
    start_button = st.button("Generate")

    if start_button:
        st.session_state.start_generation = True

    # if imgbb_api_key and model_file and garment_file and st.session_state.start_generation:
    #     model_img = Image.open(model_file)
    #     garment_img = Image.open(garment_file)
        
    #     col1, col2 = st.columns(2)
    #     with col1:
    #         st.image(model_img, caption='Model Image', use_column_width=True)
    #     with col2:
    #         st.image(garment_img, caption='Garment Image', use_column_width=True)

    #     with st.spinner('Uploading images...'):
    #         model_url = upload_image_to_imgbb(model_img, imgbb_api_key)
    #         garment_url = upload_image_to_imgbb(garment_img, imgbb_api_key)

    #     if model_url and garment_url:
    #         st.success("Images uploaded successfully!")
            
    #         download_garment = requests.get(garment_url)
    #         garment_img = Image.open(io.BytesIO(download_garment.content))
    #         garment_img_data = garment_file.getvalue()
    #         garment_img.save("garment.png")
    #         garment_desc = caption_img(garment_img_data)[0]["generated_text"]
    #         os.remove("garment.png")

    #         with st.spinner('Processing virtual try-on...'):
    #             result_url = virtual_tryon(model_url, garment_url, garment_desc)
            
    #         if result_url:
    #             st.image(result_url, caption='Virtual Try-on Result', use_column_width=True)
                
    #             response = requests.get(result_url)
    #             if response.status_code == 200:
    #                 st.download_button(
    #                     label="Download Result Image",
    #                     data=response.content,
    #                     file_name="virtual_tryon_result.png",
    #                     mime="image/png"
    #                 )
    #             else:
    #                 st.error("Failed to prepare download for the result image.")
    if model_file and garment_file and st.session_state.start_generation:
    try:
        model_img = Image.open(model_file)
        garment_img = Image.open(garment_file)
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(model_img, caption='Model Image', use_column_width=True)
        with col2:
            st.image(garment_img, caption='Garment Image', use_column_width=True)
        
        with st.spinner('Uploading images...'):
            model_url = upload_image_to_imgbb(model_img, imgbb_api_key)
            garment_url = upload_image_to_imgbb(garment_img, imgbb_api_key)

        if model_url and garment_url:
            st.success("Images uploaded successfully!")
            
            download_garment = requests.get(garment_url)
            garment_img = Image.open(io.BytesIO(download_garment.content))
            garment_img_data = garment_file.getvalue()
            garment_img.save("garment.png")
            garment_desc = caption_img(garment_img_data)[0]["generated_text"]
            os.remove("garment.png")

            with st.spinner('Processing virtual try-on...'):
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
                    logging.error(f"Failed to download result image. Status code: {response.status_code}")
                    st.error("Failed to prepare download for the result image.")
            else:
                logging.error("Virtual try-on failed to produce a result URL")
                st.error("Virtual try-on process failed. Please try again.")
        else:
            logging.error("Failed to upload images to ImgBB")
            st.error("Failed to upload images. Please try again.")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        st.error(f"An error occurred: {str(e)}") 

if __name__ == "__main__":
    main()