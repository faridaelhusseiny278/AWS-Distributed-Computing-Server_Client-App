import streamlit as st
import socket
from PIL import Image
import numpy as np
import cv2
import io
import subprocess
import sys
from io import BytesIO
import os
import time
# Global download path 
download_path = "Processed Images"
BUFFER_SIZE = 4096
  
    # Create the download folder if it doesn't exist
if not os.path.exists(download_path):
    os.makedirs(download_path)  # Create directories recursively

def Check_if_user_removed_files(processed_images, uploaded_files):
    files_names = [f.name for f in uploaded_files]
    keys_to_remove = []
    for key in processed_images:
        
        if key.split("processed_image_")[1] not in files_names:
            keys_to_remove.append(key)

    for name in keys_to_remove:
        processed_images.pop(name)

    return processed_images


operations_dict = {
        "Edge Detection": 1,
        "Color Manipulation": 2,
        "Corner Detection": 3,
        "sift_feature_detection":4,
        "denoise_image":5,
        "erosion":6,
        "dilation":7,
        "histogram_equalization":8
    }


def main():
    """
    This functions is used to initialize the variables and the socket connection only once!
    """
    @st.cache_resource
    def connect_with_retry(ip, port, retries=5, delay=5):
        attempt = 0
        while attempt < retries:
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((ip, port))
                print("Connected to server")
                return client
            except (socket.error, socket.timeout) as e:
                print(f"Connection failed with error: {e}")
                attempt += 1
                if attempt < retries:
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print("All retries failed. Exiting.")
                    return None
                
                
    @st.cache_resource
    def vars_init():
            processed_images = {}
            images_operation = {}
            client = connect_with_retry('13.51.196.249', 55548, retries=10, delay=10)

            return processed_images,images_operation,client
    
    def show_accomplished_gif():
            st.markdown("![Alt Text](https://media.giphy.com/media/8UF0EXzsc0Ckg/giphy.gif?cid=790b7611cr1xo3sscsluohoyjzhvb665qcyk50iafmaqnq59&ep=v1_gifs_search&rid=giphy.gif&ct=g)")        

    def show_close_connection_gif():
         st.markdown("![Alt Text](https://media.giphy.com/media/mVJ5xyiYkC3Vm/giphy.gif?cid=790b7611fh3u7z8net0h0f2k2z728wu4v1322t978hvwxj50&ep=v1_gifs_search&rid=giphy.gif&ct=g)")



    def download_image(processed_image, name):

        image_bytes=bytes(processed_image)

        

        # Save image with error handling
        try:
            with open(os.path.join(download_path, name), 'wb') as f:
                f.write(image_bytes)
            #print(f"Image saved: {filename}")
            st.success(f"Image saved: {name}")
        except Exception as e:
            print(f"Error saving image: {e}")


    
    
    processed_images,images_operation,client = vars_init()
    #print(f"processed_images reseeeeet: {processed_images}")
    global_process_flag = False
    process_flag = False
    operation = False
    global_operation = False

    # Force streamlit dark mode: -
    st.markdown(
        """
        <style>
        body {
            background-color: #2F2F2F;
        }
        </style>
        """,
        unsafe_allow_html=True)

    # Streamlit app
    st.title("Image Processing App 🤖")

    tab1=st.tabs(["Main Page"])
   
    
    uploaded_files = st.file_uploader("Upload Image(s)", accept_multiple_files=True, type=["jpg", "jpeg", "png"])

    with st.sidebar:
                st.title("Global Operations 🌐")
                st.write("Select an Operation to All Images!")
                with st.expander("Select Global Operation"):
                    
                    global_operation = st.radio(f"Operations: -", operations_dict.keys() , index=None, key="global_Operation")
                global_process_flag = st.button("Process All Images🥷", key="global_process")
                global_download_btn = st.button("Download All Images🥷", key="global_download")
                
                
                if global_process_flag and not global_operation:
                    st.warning("Please select an operation first!")
                elif global_process_flag and not uploaded_files:
                    st.warning("Please upload an image first!")
                elif global_process_flag:
                    process_flag = False
                    #operation   = False
                
                st.write("--------------------------- ")
                close_connection=st.button("Close Connection", key="close_connection")

                if close_connection:
                    
                    print("Closing connection.........")
                    client.send(b"Close_Connection")
                    time.sleep(2)
                    client.close()
                    show_close_connection_gif()
                    sys.exit(0)

    st.write("--------------------------- ")
    
    if uploaded_files:
        
        # add all processed images to a dictionary
        for idx, uploaded_file in enumerate(uploaded_files):
            file_name = uploaded_file.name
            if idx!=0:
                st.write("--------------------------- ")
                
            with st.expander(f"Select Operation for Image {idx+1}"):
                    operation = st.radio(f"Operations: -", operations_dict.keys(), index=None, key = idx+1)
                    process_flag = st.button("Process Image", key=f"{idx+1}_process")
                    if process_flag:
                         global_operation = False
                         global_process_flag = False
                        

            col1, col2 = st.columns(2)
            image = Image.open(uploaded_file)

            

            with col1:
                st.image(image, caption=f"Original Image {file_name}", use_column_width=True)

            # to display global processed images

            if f"processed_image_{file_name}" in processed_images.keys():
                with col2:
                    st.image(processed_images[f"processed_image_{file_name}"], caption=f"Processed Image {idx+1} ({operation or global_operation})", use_column_width=True)
                    # pop the key corresponding value: -

            # For global processing and specific Operations
            if operation:
                images_operation[file_name] = operation
            if process_flag:
                
                if operation:

                    file_data = uploaded_file.read(BUFFER_SIZE)

                    # Reset the file pointer to the beginning
                    uploaded_file.seek(0)
                    
                    # Read the file in chunks and send it
                    while True:
                        file_data = uploaded_file.read(BUFFER_SIZE)
                        if not file_data:
                            print("file data is finished!")
                            break
                        client.sendall(file_data)
                    print("file data sent!")

                    client.send(b"###%Image_Sent%")
                    msg = client.recv(BUFFER_SIZE)
                    print(msg)

                    print("image is sent to the server")
                    bar = st.progress(50)


                    if msg == b"I got the file":
                        client.send(str(operations_dict[operation]).encode())
                    client.send(b"###%Image_End%")


                    print("operation is sent to the server!")
                    bar.progress(75)

                    file_buffer = io.BytesIO()  # Create an in-memory bytes buffer

                    while True:
                        recv_data = client.recv(BUFFER_SIZE)
                        file_buffer.write(recv_data)
                        
                        if b"###%Image_Sent%" in recv_data:
                            end_image = recv_data.split(b"###%Image_Sent%")
                            if len(end_image[0]) > 0:
                                file_buffer.write(end_image[0])
                            client.send(b"I got the file")
                            print(f"Image {idx+1} is received!")
                            break
                    file_buffer.seek(0)
                    file_content = file_buffer.read()
                    processed_image = file_content

                    bar.progress(100)

                    st.success("Processed Image Received✅")
                    
                    with col2:
                        st.image(processed_image, caption=f"Processed Image {idx+1} ({operation})", use_column_width=True)
                        
                    image_bytes=bytes(processed_image)
                    # Add download button for processed image
                    st.download_button(
                        label=f"Download Processed Image 🤖",
                        data=image_bytes,
                        file_name=f"processed_image_{idx+1}.jpg"
                    )
                    show_accomplished_gif()    
                else:
                    st.warning("Please select an operation!")

        if global_process_flag and (global_operation or operation):
            print("\nglobaaal processss!!")
            
            num_files = len(uploaded_files)
            bar = st.progress(0)
            for idx, uploaded_file in enumerate(uploaded_files):
                file_data = uploaded_file.read(BUFFER_SIZE)
                file_name = uploaded_file.name
                # Reset the file pointer to the beginning
                uploaded_file.seek(0)
                
                # Read the file in chunks and send it
                while True:
                    file_data = uploaded_file.read(BUFFER_SIZE)
                    
                    if not file_data:
                        print(f"file[{idx+1}] data is finished!")
                        break
                    client.sendall(file_data)
                print("file data sent!")

                client.send(b"###%Image_Sent%")
                msg = client.recv(BUFFER_SIZE)
                print(msg)

                if msg == b"I got the file":
                    if file_name in images_operation.keys():
                        client.send(str(operations_dict[images_operation[file_name]]).encode())
                    else:
                        client.send(str(operations_dict[global_operation]).encode())
                bar.progress(int(((idx+1)/num_files)*50))

            s1 = st.success("Images are sent to the server")
            
            
            client.send(b"###%Image_End%")
            
            print("Images is sent to the server")
            flag = False

            # El touch btaaa3yy
            with st.spinner(text="Recieving Processed Images from the Server..."):
                for idx, uploaded_file in enumerate(uploaded_files):
                    file_name = uploaded_file.name
                    file_buffer = io.BytesIO()  # Create an in-memory bytes buffer
                    flag =False
                    while True:
                            recv_data = client.recv(BUFFER_SIZE)
                            file_buffer.write(recv_data)
                            
                            while recv_data:
                                recv_data = client.recv(BUFFER_SIZE)
                                file_buffer.write(recv_data)
                                if b"###%Image_Sent%" in recv_data:
                                            end_image = recv_data.split(b"###")
                                            if len(end_image[0])>0:
                                                file_buffer.write(end_image[0])
                                                client.send(b"I got the file")
                                                flag = True
                                                break
                            if flag:
                                break


                    file_buffer.seek(0)
                    file_content = file_buffer.read()
                    processed_image = file_content
                    processed_images[f"processed_image_{file_name}"] = processed_image
                    
                    bar.progress(50 + int(((idx+1)/num_files)*50))
            s1.empty()
            st.success("Processed Images Received✅")
            
            st.button("Show Processed Images 🤖", key="Show_Processed_Images")
            show_accomplished_gif()
            


        if global_download_btn:

            # Size of processed_images
            print(f"size of processed_images: {len(processed_images)}")

            # Download all processed images to my computer and ask where to download it: -
            print(f"number of uploaded_files: {len(uploaded_files)}")
            with st.status("Downloading Images") as s:
                processed_images = Check_if_user_removed_files(processed_images, uploaded_files)
                for name, processed_image in processed_images.items():
                    download_image(processed_image, name)
                s.update(label="Download Completed✅")

                 
        global_process_flag = False
        process_flag = False
        #operation = False
        global_operation =  False
        

#main()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'run':
        main()
    else:
        subprocess.run(['streamlit', 'run', sys.argv[0], 'run'])

