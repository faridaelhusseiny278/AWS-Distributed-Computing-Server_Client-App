import io   
import os
from PIL import Image
import socket
import cv2
import numpy as np

def edge_detection(img,threshold1=80, threshold2=160):
        grayscale_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        edges = cv2.Canny(grayscale_image, threshold1, threshold2)

        processed_image = Image.fromarray(edges)
        return processed_image

def color_manipulation(img):
        inverted_image = cv2.bitwise_not(img)
        processed_image = Image.fromarray(inverted_image)
        return processed_image


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # = ip

#server.bind(('0.0.0.0',50123))
server.bind(('172.31.32.142',50321))
server.listen()
BUFFER_SIZE = 4096


client_exist = False



while True:
    #client_socket, _ = server.accept()
    if not client_exist:
        client_socket, _ = server.accept()
        print("Client Connected.....")
        client_exist = True
        operation =None
        new_image = False

    file_stream = io.BytesIO()

    # Rececving New Image Section #
    
    if not new_image: 
        recv_data = client_socket.recv(BUFFER_SIZE)
        while recv_data:
                
                if recv_data ==b"new_image":
                    client_socket.send(b"new_image_ok")
                    print("New image request!")
                    break
                recv_data = client_socket.recv(BUFFER_SIZE)

    # Rececving New Image Section #
    recv_data = client_socket.recv(BUFFER_SIZE)
    while recv_data:
            print("Doing (",recv_data,") operation...")
            if recv_data == b"Edge_detection":
                operation = 1
                client_socket.send(b"Operation_ok")
                break
            elif recv_data == b"color_manipulation":
                operation = 2
                client_socket.send(b"Operation_ok")
                break
            recv_data = client_socket.recv(BUFFER_SIZE)

    recv_data = client_socket.recv(BUFFER_SIZE)
    #print(recv_data)
    while recv_data:
        file_stream.write(recv_data)
        recv_data = client_socket.recv(BUFFER_SIZE)

        if b"###%Image_Sent%" in recv_data:
                    end_image = recv_data.split(b"###")
                    if len(end_image[0])>0:
                        #print("image = ",len(end_image[0]))
                        #print("1) server recv b3d =",end_image[1])
                        file_stream.write(end_image[0])
                        
                    break
                         
    
    # Convert BytesIO object to numpy array
    file_stream.seek(0)  # Move to the beginning of the stream
    image_data = np.frombuffer(file_stream.getvalue(), dtype=np.uint8)

    # Decode image using OpenCV
    image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

    if operation == 1:
         image = edge_detection(image)
         print("Edge Detection Done!")
    elif operation == 2:
         image = color_manipulation(image)
         print("Color Manipulation Done!")

    image.save('server_file.jpeg', format='JPEG')

    with open('server_file.jpeg','rb') as file:
        file_data =file.read(BUFFER_SIZE)

        while file_data:
            client_socket.send(file_data)
            file_data = file.read(BUFFER_SIZE)

    client_socket.send(b"###%Image_Sent%")
    
    os.unlink('server_file.jpeg')


    file.close()
    print("Processed Image Sent back ^^")
    #client_socket.close()
    recv_data = client_socket.recv(BUFFER_SIZE)
    while recv_data:
        if b"new_image" in recv_data:
                print("Server new image!")
                new_image=True
                client_socket.send(b"new_image_ok")
                break
        if b"Close_Connection" in recv_data:
                client_socket.close()
                operation =None
                client_exist = False
                new_image = False
                print("Client Closed Connection!")
                break
        recv_data = client_socket.recv(BUFFER_SIZE)

        