import subprocess
import threading
import time
import os
import boto3
import sys
import socket
import queue
import io
import numpy as np
import cv2
# from project import *
from ec2_file import *
import pickle
count_consecutive_count_alive_1 = 0
count_alive = 1
alive_instances = ['master']
dead_instances = []
lock = threading.Lock()
handle_client_lock = threading.Lock()
flag = False

# Event to signal when there are alive instances
alive_event = threading.Event()
queue_ready_event = threading.Event()
send_data_done_event = threading.Event()
task_queue = queue.Queue()
original_task_queue = queue.Queue()


def check_close_connection(recv):
    if b"Close_Connection" in recv:
        client_socket.close()
        print("Bye!")
        sys.exit(0)
    return False




def save_data(data, filename):
    with open(filename, "wb") as file:
        pickle.dump(data, file)
def load_data(filename):
    with open(filename, "rb") as file:
        data = pickle.load(file)
    return data
def send_all_images(client_socket, counter):
    print("now sending all images")
    for j in range(counter):
        with open(f'server_file_{j + 1}.jpeg', 'rb') as file:
            file_data = file.read(BUFFER_SIZE)
            print(f"now trying to send image {j + 1}")
            while file_data:
                client_socket.send(file_data)
                print(f"sending image {j + 1}")
                file_data = file.read(BUFFER_SIZE)

            client_socket.send(b"###%Image_Sent%")
            print("sent image")

            recv = client_socket.recv(BUFFER_SIZE)
            print(f"received {recv}")
            check_close_connection(recv)

            if recv == b"I got the file":
                print(f"Processed Image {j + 1} Sent back")
                continue
    os.remove("first_time.pkl")
    
    return True

    

def handle_client(client_socket, flag,counter_first=0):
    global task_queue, original_task_queue, handle_client_lock
    
    while True:
        send_data_done_event.wait()
        send_data_done_event.clear()
        print(f"send_data_done_event 2  is {send_data_done_event.is_set()}")
        
        print("now handling client")
        handle_client_lock.acquire()

        tasks = []
        task_queue = queue.Queue() 
         
        recv_data = client_socket.recv(BUFFER_SIZE)
        check_close_connection(recv_data)

        file_stream = io.BytesIO()
        file_stream.write(recv_data)
        id_counter = 0
        while b'###%Image_End%' not in recv_data:
            try:
                recv_data = client_socket.recv(BUFFER_SIZE)
                check_close_connection(recv_data)
            except ConnectionResetError:
                print("Client Closed Connection")

            file_stream.write(recv_data)
            if b"###%Image_Sent%" in recv_data:
                end_image = recv_data.split(b"###")
                if len(end_image[0]) > 0:
                    file_stream.write(end_image[0])

                client_socket.send(b"I got the file")

                recv = client_socket.recv(BUFFER_SIZE)
                check_close_connection(recv)

                operation = recv

                file_stream.seek(0)
                image_data = np.frombuffer(file_stream.getvalue(), dtype=np.uint8)

                image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
                tasks.append((image, int(operation), id_counter))
                id_counter += 1
                file_stream = io.BytesIO()

        tasks.append(None)
        for task in tasks:
            task_queue.put(task)
            original_task_queue.put(task)

        save_data(tasks, "first_time.pkl")
        handle_client_lock.release()
        queue_ready_event.set()
        print("All tasks received from client")
        print(f"flag is {flag}")
        print(f"task queue size is received from clienttttt {task_queue.qsize()}")

       
        if os.path.exists("processed_images.pkl"):
            os.remove("processed_images.pkl")
        
        send_data_done_event.set()
        print(f"send_data_done_event is {send_data_done_event.is_set()}")
        counter_first+=1
        print(f"counter_first is {counter_first}")
        if counter_first > 1:
            time.sleep(5)
            handle_client_thread = threading.Thread(target=handle_client, args=(client_socket, flag,counter_first))
            handle_client_thread.daemon = True
            handle_client_thread.start()
            mpi_command = ["mpirun", "-n", str(count_alive), "-host", ",".join(alive_instances), "--enable-recovery", "python3", "project.py"]
            mpi_process = subprocess.run(mpi_command)
            print("i am heree!!")
           
        time.sleep(5)
        
        
        
        

def send_data(client_socket, data):
    global lock
    
    print("I am in send data now")
    while True:
        print("waiting for send_data_done_event")
        send_data_done_event.wait()
        print("send_data_done_event is set")
        send_data_done_event.clear()
        print("send_data_done_event is cleared")
        lock.acquire()
        task_queue = queue.Queue()
        counter = 0
        queue_ready_event.wait()
        if os.path.exists("first_time.pkl"):
            tasks = load_data("first_time.pkl")
        else:
            lock.release()
            continue
        for task in tasks:
            task_queue.put(task)

        print(f"Task Queue Size: {task_queue.qsize()}")

        for j in range(task_queue.qsize() - 1):
            while not os.path.exists(f'server_file_{j + 1}.jpeg'):
                time.sleep(1)
                pass
            print(f"server_file_{j + 1}.jpeg found")
            counter += 1
        if counter == task_queue.qsize() - 1:
            print("All images processed")
            print(f"lock state is {lock.locked()}")

            print(f"counter is {counter}")
            print(f"now calling send_all_images")
            if send_all_images(client_socket, counter):
                for j in range(counter):
                    os.remove(f'server_file_{j + 1}.jpeg') 

            print("resetting the task queue")

            lock.release()
            send_data_done_event.set()
            time.sleep(5)

            



def check_and_start_instances():
    global count_alive, alive_instances, dead_instances, alive_event,flag
    while True:
        
        print("Checking for alive instances..")
        alive_instances = ['master']
        dead_instances = []
        count_alive = 1
        failed_instance = None
        if os.path.exists("failed_in_the_middle.txt"):
            print("Failed in the middle!!!!!")
            with open("failed_in_the_middle.txt", "r") as file:
                # read the file contents and check if it is 1
                failed_instance = file.read().strip()
        if failed_instance=="1":
            # delete the file contents and write 0 instead
            with open("failed_in_the_middle.txt", "w") as file:
                file.write("0")
            print("wrote 0")
            flag = False
            

        
        for hostname, instance_id in instance_ids.items():
            if is_instance_healthy(instance_id):
                count_alive += 1
                alive_instances.append(hostname)
            else:
                dead_instances.append(hostname)
        print(f"Alive instances are: {alive_instances}")
        print(f"Dead instances are: {dead_instances}")
        # No instances are alive
        if count_alive == 1:
            
            for dead_instance in dead_instances:
                instance_id = instance_ids.get(dead_instance)
                if instance_id:
                    print(f"Starting instance {instance_ids[dead_instance]}")  
                    if start_instance(instance_id):
                        count_alive += 1
                        alive_instances.append(dead_instance)
                        alive_event.set()  # Set the event to signal that there are alive instances
                        if flag == False:
                     
                            time.sleep(20)
                            # subprocess.run(["killall", "mpirun"])
                         
                            print("No instances are alive. Exiting the program")
                            print(f"Alive instances are: {alive_instances}")
                            send_data_thread=  threading.Thread(target=send_data, args=(client_socket, task_queue))
                            send_data_thread.daemon = True
                            send_data_thread.start()
                            
                            subprocess.run(["mpirun", "-n", str(count_alive), "-host", ",".join(alive_instances), "--enable-recovery", "python3", "project.py"])
                            # start_mpi= threading.Thread(target=start_mpi_process)
                            # start_mpi.start()

                            

                            print("flag is true")
                            
                            flag= True
                            continue
                    else:
                        continue
        else:
            alive_event.set()
        
        time.sleep(20)  # Check every 20 seconds

check_thread = threading.Thread(target=check_and_start_instances)
check_thread.daemon = True  # Set the thread as daemon so it will exit when the main program exits
check_thread.start()



alive_event.wait()
BUFFER_SIZE = 4096
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
server.bind(('0.0.0.0',55548))
server.listen()
print("Server is listening..")
client_socket, _ = server.accept()
print(f"Connection from {client_socket.getpeername()} accepted")

# task_queue= handle_client(client_socket,False)

send_data_done_event.set()

handle_client_thread = threading.Thread(target=handle_client, args=(client_socket,False))
handle_client_thread.daemon = True
handle_client_thread.start()

send_data_thread=  threading.Thread(target=send_data, args=(client_socket, task_queue))
send_data_thread.daemon = True
send_data_thread.start()

queue_ready_event.wait()
print("Starting the MPI process")

mpi_command = ["mpirun", "-n", str(count_alive), "-host", ",".join(alive_instances), "--enable-recovery", "python3", "project.py"]

mpi_process = subprocess.run(mpi_command)



