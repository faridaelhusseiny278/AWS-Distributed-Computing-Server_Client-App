import socket
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import cv2
import sys
import os
# Define global variables
filename = None
original_image = None

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # = ip
#client.connect(('16.171.147.7', 50321))    # ec2 instance server
client.connect(('127.0.0.1', 50321))


BUFFER_SIZE = 4096

# Creating Folder for Processed Images ^^
folder_name = "Processed Images"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)


def upload_image():
    global filename, original_image
    filename = filedialog.askopenfilename(initialdir="/", title="Select Image",filetypes=(("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")))
    original_image = cv2.imread(filename)
    show_image(filename)

    
def show_image(image_name):

    img = Image.open(image_name)
    
    img.thumbnail((250, 250))  # Resize image for display
    img = ImageTk.PhotoImage(img)
    label_img.config(image=img)
    label_img.image = img

def close_app():
    client.send(b"Close_Connection")
    client.close()
    print("Bye!")
    sys.exit(0)  # You can replace 0 with any other integer value as needed


def process_image():
    global filename, original_image

    selected_operation = operation_var.get()
    client.send(b"new_image")
    print("Sent New image Request!")
    recv_data = client.recv(BUFFER_SIZE)
    
    while recv_data:
            if recv_data ==b"new_image_ok":
                print("Image OK!")
                break
            recv_data = client.recv(BUFFER_SIZE)

    if selected_operation == 1:
        Operation_done = "Edge_detection"
        client.send(b"Edge_detection")
    elif selected_operation ==2:
        Operation_done = "color_manipulation"
        client.send(b"color_manipulation")
    
    recv_data = client.recv(BUFFER_SIZE)

    while recv_data:
            if recv_data ==b"Operation_ok":
                break
            recv_data = client.recv(BUFFER_SIZE)

    with open(filename, 'rb') as file:

        file_data = file.read(BUFFER_SIZE)

        while file_data:
            client.send(file_data)
            file_data = file.read(BUFFER_SIZE)

    client.send(b"###%Image_Sent%")
    #print("Image Sent!")



    # Extract the filename without the extension
    file_name_without_extension = filename.split("/")[-1].split(".")[0]
    extention =filename.split("/")[-1].split(".")[1]
    image_name =f'{file_name_without_extension}_{Operation_done}.{extention}'
    print(image_name)
        # Construct the full file path
    file_path = os.path.join(folder_name, image_name)
    with open(file_path, 'wb') as file:
        recv_data = client.recv(BUFFER_SIZE)
        
        while recv_data:
                file.write(recv_data)
                recv_data = client.recv(BUFFER_SIZE)
                if b"###%Image_Sent%" in recv_data:
                         end_image = recv_data.split(b"###")
                         file.write(end_image[0])
                         #print("Client recv b3d =",end_image[1])
                         break  
    show_image(file_path)


    file.close()
    print("Processed Image Recevied ^^")


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
