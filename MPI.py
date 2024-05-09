import threading
import queue
from mpi4py import MPI  # MPI for distributed computing
import io   
import os
import socket
import cv2
import numpy as np
import threading
from Image_Processing import edge_detection, color_manipulation
from PIL import Image
import cv2


class WorkerThread(threading.Thread):
    def __init__(self, comm, task_queue):
        threading.Thread.__init__(self)
        self.task_queue = task_queue
        self.comm = comm

    def run(self):
                image, operation = self.task_queue
                print(f"Worker {self.comm.Get_rank()} is now processing task.{self.task_queue}")
                
                result = self.process_image(image, operation)
                print(f"result is now preprocessed by worker {self.comm.Get_rank()}")
                self.comm.send(result, dest=0)

    def process_image(self, image, operation):
        if operation == 1:
            result = edge_detection(image)
        elif operation == 2:
            result = color_manipulation(image)
        return result
 

    def edge_detection(img,threshold1=90, threshold2=180):
            grayscale_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            edges = cv2.Canny(grayscale_image, threshold1, threshold2)

            processed_image = Image.fromarray(edges)
            return processed_image

    def color_manipulation(img):
            inverted_image = cv2.bitwise_not(img)
            processed_image = Image.fromarray(inverted_image)
            return processed_image


task_queue = queue.Queue()
def handle_client(client_socket):
    operation = None
    new_image = False
    file_stream = io.BytesIO()
    while True:

        if not new_image: 
            recv_data = client_socket.recv(BUFFER_SIZE)
            while recv_data:
                    
                    if recv_data ==b"new_image":
                        client_socket.send(b"new_image_ok")
                        print("New image request!")
                        break
                    recv_data = client_socket.recv(BUFFER_SIZE)

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
        while recv_data:
            file_stream.write(recv_data)
            recv_data = client_socket.recv(BUFFER_SIZE)

            if b"###%Image_Sent%" in recv_data:
                        end_image = recv_data.split(b"###")
                        if len(end_image[0])>0:
                            file_stream.write(end_image[0])
                            
                        break
                            
        
        file_stream.seek(0)  
        image_data = np.frombuffer(file_stream.getvalue(), dtype=np.uint8)
        image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
        
       
        tasks= [(image, operation),(None)]
        for task in tasks:
            task_queue.put(task)

    
        return task_queue

        

if MPI.COMM_WORLD.Get_rank() == 0:

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # = ip
    server.bind(('0.0.0.0',50321))
    server.listen()
    BUFFER_SIZE = 4096
    print("Server is listening for connections.....")
    while True:
        client_socket, _ = server.accept()
        print(f"Client {client_socket.getpeername()} connected.")
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()
        
     
        #distribute each task to a worker
        num_workers = MPI.COMM_WORLD.Get_size() 
        
        for i in range(1, num_workers):
                task = task_queue.get()
                if task is not None:
                    MPI.COMM_WORLD.send(task, dest=i)
                else:
                    break
            
           

        print("Master waiting for result from worker...")
        for i in range(1, num_workers):
            image = MPI.COMM_WORLD.recv(source=i)
            print("Master received result from worker...", image)

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

        recv_data = client_socket.recv(BUFFER_SIZE)
        if b"Close_Connection" in recv_data:
                print(f"Client {client_socket.getpeername()} Closed Connection!")
                client_socket.close()
                break
        

else:
                task_queue = MPI.COMM_WORLD.recv(source=0)
                print("Worker", MPI.COMM_WORLD.Get_rank(), "received task", task_queue)
                WorkerThread(MPI.COMM_WORLD, task_queue).start()



    
               