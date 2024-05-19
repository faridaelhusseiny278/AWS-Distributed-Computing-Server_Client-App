import socket
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import cv2
import sys
import numpy as np
import os
import json
filename = None
original_image = None

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # = ip
client.connect(('EC2 IPP', YOUR PORT))    # ec2 instance server
original_images = []
image_operations = []

BUFFER_SIZE = 4096

folder_name = "Processed Images"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)


def upload_image():
    global original_images, image_operations
    filenames = filedialog.askopenfilenames(initialdir="/", title="Select Images", filetypes=(("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")))
    print(f"filename: {filenames}")
    for filename in filenames:
        with open(filename, 'rb') as file:
            image_data = file.read()
        original_images.append(image_data)
        image_operations.append((filename, None))


def close_app():
    client.send(b"Close_Connection")
    client.close()
    print("Bye!")
    sys.exit(0)  



def process_image():
    global image_operations
    print(f"Image Operations: {image_operations}")

    for i, (filename, operation) in enumerate(image_operations):        
            operation = int(input(f"Enter the operation (1 for Edge Detection, 2 for Color Manipulation) for image {i}: "))
            
            image_operations[i] = (filename, operation)
    print(f"Image Operations: {image_operations}")

    for i, (filename, operation) in enumerate(image_operations):
            with open(filename, 'rb') as file:
                file_data = file.read(BUFFER_SIZE)

                while file_data:
                    client.send(file_data)
                    file_data = file.read(BUFFER_SIZE)
                client.send(b"###%Image_Sent%")
                msg = client.recv(BUFFER_SIZE)
                print(msg)
                if msg == b"I got the file":
                    client.send(str(operation).encode())

    client.send(b"###%Image_End%")
    print("All files sent successfully from client side")
    print("image operations, ", image_operations)
    for i, (filename, operation) in enumerate(image_operations):
        file_name_without_extension = filename.split("/")[-1].split(".")[0]
        extention = filename.split("/")[-1].split(".")[1]
        image_name = f"{file_name_without_extension}_{operation}.{extention}"
        print(image_name)
        file_path = os.path.join(folder_name, image_name)
        with open(file_path, 'wb') as file_stream:
            recv_data = client.recv(BUFFER_SIZE)
            file_stream.write(recv_data)
            while recv_data:
                recv_data = client.recv(BUFFER_SIZE)
                file_stream.write(recv_data)
                if b"###%Image_Sent%" in recv_data:
                            end_image = recv_data.split(b"###")
                            if len(end_image[0])>0:
                                file_stream.write(end_image[0])
                                client.send(b"I got the file")
                                break 
               

    print("All files received and saved successfully from server side")

        

# Main GUI window
root = tk.Tk()
root.title("Image Processing App")

upload_frame = tk.Frame(root)
upload_frame.pack(pady=10)

upload_button = tk.Button(upload_frame, text="Upload Image", command=upload_image)
upload_button.pack(side=tk.LEFT, padx=10)

operation_frame = tk.Frame(root)
operation_frame.pack(pady=10)

operation_var = tk.IntVar()
operation_var.set(1)

operation_label = tk.Label(operation_frame, text="Select Operation:")
operation_label.pack(side=tk.LEFT, padx=10)

edge_radio = tk.Radiobutton(operation_frame, text="Edge Detection", variable=operation_var, value=1)
edge_radio.pack(side=tk.LEFT)

color_radio = tk.Radiobutton(operation_frame, text="Color Manipulation", variable=operation_var, value=2)
color_radio.pack(side=tk.LEFT)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

go_button = tk.Button(button_frame, text="Go", command=process_image)
go_button.pack(side=tk.LEFT, padx=10)

close_button = tk.Button(button_frame, text="Close Connection", command=close_app)
close_button.pack(side=tk.LEFT)

image_frame = tk.Frame(root)
image_frame.pack(pady=10)

label_img = tk.Label(image_frame)
label_img.pack()

root.mainloop()
