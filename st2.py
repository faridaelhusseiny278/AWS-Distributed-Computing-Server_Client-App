import streamlit as st
from PIL import Image
import numpy as np
import cv2
import io
import subprocess
import sys
from io import BytesIO
import os

# Global download path 
download_path = "Processed Images"
    
    # Create the download folder if it doesn't exist
if not os.path.exists(download_path):
    os.makedirs(download_path)  # Create directories recursively

def main():

    def Check_if_user_removed_files(processed_images, uploaded_files):
        files_names = [f.name for f in uploaded_files]
        keys_to_remove = []
        for key in processed_images:
            
            if key.split("processed_image_")[1] not in files_names:
                keys_to_remove.append(key)
                
                


        for name in keys_to_remove:
            processed_images.pop(name)
        
        return processed_images


    def download_image(processed_image, name):
        img_byte_arr = io.BytesIO()
        Image.fromarray(processed_image).save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        

        # Save image with error handling
        try:
            with open(os.path.join(download_path, name), 'wb') as f:
                f.write(img_byte_arr)
            #print(f"Image saved: {filename}")
            st.success(f"Image saved: {name}")
        except Exception as e:
            print(f"Error saving image: {e}")



    @st.cache_resource
    def vars_init():
        processed_images = {}
        return processed_images	
    
    processed_images = vars_init()
    global i
    global_process_flag = False
    process_flag = False
    operation = False
    global_operation = False

    def edge_detection(image):
        gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        return edges

    def color_manipulation(image):
        gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)

    def process_image(image, operation):
        if operation == "Edge Detection":
            return edge_detection(image)
        elif operation == "Color Manipulation":
            return color_manipulation(image)

    # Streamlit app
    st.title("Image Processing App 🤖")
    tab1=st.tabs(["Main Page"])
   
    
    uploaded_files = st.file_uploader("Upload Image(s)", accept_multiple_files=True, type=["jpg", "jpeg", "png"])
    print(f"uploaded_files: {uploaded_files}")
    with st.sidebar:
                st.title("Global Operations 🌐")
                st.write("Select an Operation to All Images!")
                with st.expander("Select Global Operation"):
                    
                    global_operation = st.radio(f"Operations: -", ["Edge Detection", "Color Manipulation"], index=None, key="global_Operation")
                    global_process_flag = st.button("Process All Images🥷", key="global_process")
                    global_download_btn = st.button("Download All Images🥷", key="global_download")
                    
                    if global_process_flag and not global_operation:
                        st.warning("Please select an operation first!")
                    elif global_process_flag and not uploaded_files:
                        st.warning("Please upload an image first!")
                    elif global_process_flag:
                        process_flag = False
                        operation   = False

    st.write("--------------------------- ")

    i = len(uploaded_files)
    if uploaded_files:
        
        # add all processed images to a dictionary
      if i>0:  
        for idx, uploaded_file in enumerate(uploaded_files):
            file_name = uploaded_file.name
            if idx!=0:
                st.write("--------------------------- ")
                
            with st.expander(f"Select Operation for Image {idx+1}"):
                    operation = st.radio(f"Operations: -", ["Edge Detection", "Color Manipulation"], index=None, key = idx+1)
                    process_flag = st.button("Process Image", key=f"{idx+1}_process")
                    if process_flag:
                         global_operation = False
                         global_process_flag = False
                        

            col1, col2 = st.columns(2)
            image = Image.open(uploaded_file)
            
            with col1:
                st.image(image, caption=f"Original Image {file_name}", use_column_width=True)

            if process_flag or global_process_flag:
                #st.write(f"you choses {operation} or global operation {global_operation}")
                if operation or global_operation:
                    
                    processed_image = process_image(image, global_operation or operation)
                    # henaa bn append
                    processed_images[f"processed_image_{file_name}"] = processed_image
                    #st.write("Progress: -")
                    bar = st.progress(50)
                    s1 = st.success("Operation Sent to the server✅")
                    s1.empty()
                # Display original and processed images side by side
                
                    
                    s2 = st.success("Processed Image Received✅")
                    #s2.empty()
                    bar.progress(75)
                    with col2:
                        bar.progress(100)
                        st.image(processed_image, caption=f"Processed Image {idx+1} ({global_operation or operation})", use_column_width=True)
                        

                    # Convert processed image to bytes
                    img_byte_arr = io.BytesIO()
                    Image.fromarray(processed_image).save(img_byte_arr, format='JPEG')
                    img_byte_arr = img_byte_arr.getvalue()
                    # Add download button for processed image
                    st.download_button(
                        label=f"Download Processed Image",
                        data=img_byte_arr,
                        file_name=f"processed_image_{idx+1}.jpg"
                    )
                else:
                    st.warning("Please select an operation!")

        if global_download_btn:
            # size of   processed_images
            
            print(f"size of processed_images: {len(processed_images)}")
            # download all processed images to my computer and ask where to download it: -
            print(f"number of uploaded_files: {len(uploaded_files)}")
            processed_images = Check_if_user_removed_files(processed_images, uploaded_files)
            for name, processed_image in processed_images.items():
                download_image(processed_image, name)
                



                       
        global_process_flag = False
        process_flag = False
        operation = False
        global_operation = False

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'run':
        main()
    else:
        subprocess.run(['streamlit', 'run', sys.argv[0], 'run'])