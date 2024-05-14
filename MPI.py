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
                print(f"Worker {self.comm.Get_rank()} is now processing task.")
                
                result = self.process_image(image, operation)
                print(f"result is now preprocessed by worker {self.comm.Get_rank()}")
                self.comm.send(result, dest=0)

    def process_image(self, image, operation):
        if operation == 1:
            result = self.edge_detection(image)
        elif operation == 2:
            result = self.color_manipulation(image)
        elif operation == 3:
            result = self.detect_corners(image)
        return result
 

    def edge_detection(self,img,threshold1=90, threshold2=180):
            grayscale_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            edges = cv2.Canny(grayscale_image, threshold1, threshold2)

            processed_image = Image.fromarray(edges)
            return processed_image

    def color_manipulation(self,img):
            inverted_image = cv2.bitwise_not(img)
            processed_image = Image.fromarray(inverted_image)
            return processed_image


    def detect_corners(self,image):
        image_array = np.array(image)
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
        else:
            gray = image_array.copy()  
        dst = cv2.cornerHarris(gray, blockSize=2, ksize=3, k=0.04)
        dst = cv2.dilate(dst, None)
        ret, thresh = cv2.threshold(dst, 0.1*dst.max(), 255, cv2.THRESH_BINARY)
        corners = np.argwhere(thresh == 255)
        image_with_corners = image_array.copy()  
        for corner in corners:
            x, y = corner[0], corner[1]
            cv2.circle(image_with_corners, (x, y), 5, (0, 0, 255), -1)
        processed_image = Image.fromarray(image_with_corners)
        return processed_image


task_queue = queue.Queue()
def handle_client(client_socket):
    
    tasks = []
    recv_data = client_socket.recv(BUFFER_SIZE)
    file_stream = io.BytesIO()
    file_stream.write(recv_data)

    while b'###%Image_End%' not in recv_data:
            recv_data = client_socket.recv(BUFFER_SIZE)
            file_stream.write(recv_data)
            if b"###%Image_Sent%" in recv_data:
                        end_image = recv_data.split(b"###")
                        if len(end_image[0])>0:
                            file_stream.write(end_image[0])

                        client_socket.send(b"I got the file")
                        operation = client_socket.recv(BUFFER_SIZE)

                        file_stream.seek(0)  
                        image_data = np.frombuffer(file_stream.getvalue(), dtype=np.uint8)
                        image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
                        tasks.append((image, int(operation)))
                        file_stream = io.BytesIO()

       
    tasks.append(None) 
    for task in tasks:
        task_queue.put(task)

    return task_queue


        
print ("My rank is ", MPI.COMM_WORLD.Get_rank(), "My hostname is ", MPI.Get_processor_name())
if MPI.COMM_WORLD.Get_rank() == 0:
    processed_images = []   

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    server.bind(('0.0.0.0',55552))
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
                    print(f"sent work to worker {i}")
                else:
                    break
            
        print("task queue size: ", task_queue.qsize())  
        for i in range(1,MPI.COMM_WORLD.Get_size()):
            print(f"Master waiting for result from worker{i}")
            image = MPI.COMM_WORLD.recv(source=i)
            processed_images.append(image)
        
            image.save(f'server_file_{i}.jpeg', format='JPEG')
            
            image = Image.open(f'server_file_{i}.jpeg')
            image_array = np.array(image)



        for i in range(1,MPI.COMM_WORLD.Get_size()): 
            with open(f'server_file_{i}.jpeg', 'rb') as file:
                file_data = file.read(BUFFER_SIZE)
                while file_data:
                    client_socket.send(file_data)
                    file_data = file.read(BUFFER_SIZE)
                client_socket.send(b"###%Image_Sent%")
                if client_socket.recv(BUFFER_SIZE) == b"I got the file":
                    continue
                      
            # os.unlink(f'server_file_{i}.jpeg')
            print(f"Processed Image {i} Sent back")


        client_socket.close() 
        break  
          

else:
                task_queue = MPI.COMM_WORLD.recv(source=0)
                print("Worker", MPI.COMM_WORLD.Get_rank(), "received task")
         
                WorkerThread(MPI.COMM_WORLD, task_queue).start()



    
               