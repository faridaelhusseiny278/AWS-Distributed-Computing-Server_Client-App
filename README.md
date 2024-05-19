# Image Processing App

## Overview

The Image Processing App is a Streamlit-based web application that allows users to upload images and apply various image processing operations. The app connects to a remote server to process the images and provides users with the ability to download the processed images.

## Features

- **Upload Multiple Images**: Users can upload multiple images in JPEG, JPG, and PNG formats.
- **Individual and Global Operations**: Users can select different image processing operations for each image or apply a single operation to all uploaded images.
- **Real-time Processing**: The app sends images to a remote server for processing and receives the processed images in real-time.
- **Download Processed Images**: Users can download individual processed images or all processed images at once.
- **GIF Feedback**: Visual feedback with GIFs is provided for actions such as connection closing and successful image processing.

## Supported Operations

The app supports the following image processing operations:

1. Edge Detection
2. Color Manipulation
3. Corner Detection
4. SIFT Feature Detection
5. Denoise Image
6. Erosion
7. Dilation
8. Histogram Equalization

## Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/yourusername/image-processing-app.git
    cd image-processing-app
    ```

2. **Install dependencies**:

    Make sure you have Python 3.7+ installed. Then, create a virtual environment and install the required packages:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3. **Run the app**:

    ```bash
    python app.py
    ```

    The app will automatically open in your default web browser.

## Usage

1. **Upload Images**:
    - Click on the "Upload Image(s)" button to upload one or more images.
    
2. **Select Operations**:
    - For individual images, expand the section for each image and select an operation from the dropdown list.
    - For applying the same operation to all images, select an operation from the sidebar under "Global Operations".

3. **Process Images**:
    - Click the "Process Image" button for individual images or "Process All Images" for global operations.
    - The app will display the original and processed images side by side.
    - If the process is completed you are expected to see this confirmation: -
      
    ![Bye_Gif](https://github.com/OmarMDiab/AWS-Distributed-Computing-Server_Client-App/blob/main/Client%20App/GIFS/Mission%20Accomplished.gif)

4. **Download Images**:
    - After processing, you can download each processed image by clicking the "Download Processed Image" button.
    - Alternatively, download all processed images at once by clicking the "Download All Images" button from the sidebar.

5. **Close Connection**:
    - To close the connection to the server, click the "Close Connection" button in the sidebar.

## Code Explanation

### Main Components

1. **Connecting to the Server**:
    - The `connect_with_retry` function establishes a socket connection to the server with retry logic.
    
    ```python
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
    ```

2. **Image Processing**:
    - The `process_image` function sends the image to the server, receives the processed image, and handles progress updates.

    ```python
    def process_image(uploaded_file, operation, client):
        file_data = uploaded_file.read(BUFFER_SIZE)
        uploaded_file.seek(0)
        while True:
            file_data = uploaded_file.read(BUFFER_SIZE)
            if not file_data:
                break
            client.sendall(file_data)
        client.send(b"###%Image_Sent%")
        msg = client.recv(BUFFER_SIZE)
        if msg == b"I got the file":
            client.send(str(operations_dict[operation]).encode())
        client.send(b"###%Image_End%")
        file_buffer = io.BytesIO()
        while True:
            recv_data = client.recv(BUFFER_SIZE)
            file_buffer.write(recv_data)
            if b"###%Image_Sent%" in recv_data:
                break
        file_buffer.seek(0)
        processed_image = file_buffer.read()
        return processed_image
    ```

3. **User Interface**:
    - The Streamlit-based UI allows users to upload images, select operations, and interact with the app.

    ```python
    def main():
        processed_images, images_operation, client = vars_init()
        st.title("Image Processing App 🤖")
        uploaded_files = st.file_uploader("Upload Image(s)", accept_multiple_files=True, type=["jpg", "jpeg", "png"])
        if uploaded_files:
            for idx, uploaded_file in enumerate(uploaded_files):
                file_name = uploaded_file.name
                with st.expander(f"Select Operation for Image {idx+1}"):
                    operation = st.radio(f"Operations: -", operations_dict.keys(), index=None, key=idx+1)
                    process_flag = st.button("Process Image", key=f"{idx+1}_process")
                    if process_flag:
                        processed_image = process_image(uploaded_file, operation, client)
                        st.image(processed_image, caption=f"Processed Image {idx+1} ({operation})", use_column_width=True)
                        st.download_button(label=f"Download Processed Image 🤖", data=processed_image, file_name=f"processed_image_{idx+1}.jpg")
    ```

### Closing Connection

To ensure the connection is properly closed:

```python
if close_connection:
    print("Closing connection.........")
    client.send(b"Close_Connection")
    time.sleep(2)
    client.close()
    show_close_connection_gif()
    sys.exit(0)
````

## Thank you
![Bye_Gif](https://github.com/OmarMDiab/AWS-Distributed-Computing-Server_Client-App/blob/main/Client%20App/GIFS/Close%20Connection.gif)
