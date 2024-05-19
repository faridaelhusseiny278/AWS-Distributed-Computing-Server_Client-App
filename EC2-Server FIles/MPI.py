import threading
import queue
from mpi4py import MPI  # MPI for distributed computing
import io   
import os
import time
import sys
import socket
import boto3
import subprocess
import pickle
import requests
import cv2
import numpy as np
import threading
# from Image_Processing import edge_detection, color_manipulation
from PIL import Image
import cv2
from Image_Preprocessing import *
from ec2_file import *

class WorkerThread(threading.Thread):
    def __init__(self, comm, task_queue):
        threading.Thread.__init__(self)
        self.task_queue = task_queue
        self.comm = comm

    def run(self):
        
            image, operation,id = self.task_queue
            result = self.process_image(image, operation)
            print(f"Result is now preprocessed by worker {self.comm.Get_rank()}")
            result = (result, id)

                

            self.comm.send(result, dest=0)


    def process_image(self, image, operation):
        if operation == 1:
            result =edge_detection(image)
        elif operation == 2:
            result =color_manipulation(image)
        elif operation == 3:
            result =detect_corners(image)
        elif operation == 4:
            result =sift_feature_detection(image)
        elif operation == 5:
            result =denoise_image(image)
        elif operation == 6:
            result =erosion(image)
        elif operation == 7:
             result =dilation(image)
        elif operation==8:
             result = histogram_equalization(image)
        return result
 



def get_hostname(received_node_info, worker_rank):
    for rank, hostname in received_node_info:
        if rank == worker_rank:
            return hostname
    return None
 

def remove_processed(task_queue, processed_images,size):

    for _ in range(size):
        item = task_queue.get()
        if item is not None:
            if (item[2] not in [processed_item[1] for processed_item in processed_images]) :
                print(f"Task {item[2]} was not processed")
                task_queue.put(item)
    return task_queue


def get_rank(received_node_info, hostname):
    for rank, host in received_node_info:
        if host == hostname:
            return rank
    return None



def load_data(filename):
    with open(filename, "rb") as file:
        return pickle.load(file)
    
def save_data(data, filename):
    with open(filename, "wb") as file:
        pickle.dump(data, file)

if MPI.COMM_WORLD.Get_rank() == 0:
    received_node_info = []
    if os.path.exists("flag_first_time.txt")== False:
        flag_first_time = True
        with open("flag_first_time.txt", "w") as file:
            file.write("1")
    else:
        flag_first_time = False
        
    while True:
        processed_images=[]
        task_queue = queue.Queue()
        original_task_queue = queue.Queue()
        if os.path.exists("first_time.pkl"):
            tasks = load_data("first_time.pkl")
        else:
            continue
    
        for task in tasks:
                task_queue.put(task)
                original_task_queue.put(task)
        # print(f"tasks are {tasks}")
        if os.path.exists("processed_images.pkl"):
            processed_images= load_data("processed_images.pkl")
        # print(f"processed images are {processed_images}")



        for i in range(1, MPI.COMM_WORLD.Get_size()):
            node_info = MPI.COMM_WORLD.recv(source=i)
            received_node_info.append(node_info)


    
        #distribute each task to a worker
        num_workers = MPI.COMM_WORLD.Get_size()
        actual_num_workers = 1
        for i in range(1, num_workers):
            if is_instance_healthy(get_instance_id(get_hostname(received_node_info,i))):
                    actual_num_workers+=1

        num_workers = actual_num_workers
            
            
    

        
        worker_index = 1
        task= task_queue.get()
        original_task_size = task_queue.qsize()
        assigned_workers = []
        print(f"Master has {task_queue.qsize()} tasks to distribute to {num_workers-1} workers")
        if task_queue.qsize()>= (num_workers-1): 
            print("tasks are greater than or equal to workers")
            for i in range(1, num_workers):
                    # if i == 1:
                    #      stop_instance(get_instance_id(get_hostname(received_node_info,i)))
                    # elif i == 2:
                    #     stop_instance(get_instance_id(get_hostname(received_node_info,i)))
                        
                
                    if is_instance_healthy(get_instance_id(get_hostname(received_node_info,i))):
                        print("sending task to worker", i)
                        MPI.COMM_WORLD.send(task, dest=i)
                        print(f"sent work to worker {get_hostname(received_node_info,i)}")
                        task = task_queue.get()
                        assigned_workers.append(i)
                
        else:
            print("tasks are less than workers")
            for i in range(task_queue.qsize()):
                
                if is_instance_healthy(get_instance_id(get_hostname(received_node_info,i+1))):
                    MPI.COMM_WORLD.send(task, dest=i+1)
                    print(f"sent work to worker {get_hostname(received_node_info,i+1)}")
                    task = task_queue.get()
                    assigned_workers.append(i+1)
                

        counter=0  
        temp_assigned_workers = assigned_workers.copy()
        for worker in assigned_workers:
            if is_instance_healthy(get_instance_id(get_hostname(received_node_info,worker))):
                timeout = 8
                start_time = time.time()
                while True:
                    if MPI.COMM_WORLD.Iprobe(source=worker):
                        print(f"Master waiting for result from worker{get_hostname(received_node_info,worker)}")
                        image,id = MPI.COMM_WORLD.recv(source=worker)
                        counter+=1
                        print(f"master received image {id} from worker {get_hostname(received_node_info,worker)}")
                        processed_images.append((image,id))
                        if flag_first_time:
                            save_data(processed_images, "processed_images.pkl")
                        print(f"processed images are {processed_images}")
                    
                        image.save(f'server_file_{counter}.jpeg', format='JPEG')
                        print(f"image saved as server_file_{counter}.jpeg")
                        temp_assigned_workers.remove(worker)
                        break

            else:
                    temp_assigned_workers.remove(worker)
                    print("matet")


        assigned_workers = temp_assigned_workers.copy()
        excess_task_queue= remove_processed(original_task_queue, processed_images, original_task_queue.qsize())
        while excess_task_queue.qsize() != 0:
            print(f"original task queue size after removing processed images is {excess_task_queue.qsize()}")
            worker_index = 1   
            print("Some tasks were not processed")
            
            for i in range(excess_task_queue.qsize()):               
                print(f"checking if worker {get_hostname(received_node_info,worker_index) } is healthy")
                unhealthy_count = 0

                while not is_instance_healthy(get_instance_id(get_hostname(received_node_info,worker_index))):
                    unhealthy_count+=1
                    if unhealthy_count > num_workers-1:
                        print("No healthy workers..waiting for 20 seconds to start new workers")
                        if os.path.exists("failed_in_the_middle.txt")==False:
                            with open("failed_in_the_middle.txt", "w") as file:
                                file.write("1")
                        time.sleep(30)
                        continue
                    print(f"worker {get_hostname(received_node_info,worker_index) } is not healthy")
                    worker_index = (worker_index + 1) % num_workers
                    if worker_index == 0:
                        worker_index = 1

                unhealthy_count = 0
                print("sending task to worker", get_hostname(received_node_info,worker_index))
                task = excess_task_queue.get()
            
                MPI.COMM_WORLD.send(task, dest=worker_index)
                        
                assigned_workers.append(worker_index)
                print(f"sent work to worker {get_hostname(received_node_info,worker_index)}")
                # task = original_task_queue.get()
                worker_index = (worker_index + 1) % num_workers
                if worker_index == 0:
                        worker_index = 1
            
            

            print("assigned workers are", assigned_workers)
            for worker in assigned_workers:
                    if is_instance_healthy(get_instance_id(get_hostname(received_node_info, worker))):
                        timeout = 8
                        start_time = time.time()
                        while True:
                            if MPI.COMM_WORLD.Iprobe(source=worker):
                                print(f"Master waiting for result from worker{get_hostname(received_node_info,worker)}")
                                image,id = MPI.COMM_WORLD.recv(source=worker)
                                counter+=1
                                print(f"master received image {id} from worker {get_hostname(received_node_info,worker)}")
                                processed_images.append((image,id))
                                if flag_first_time:
                                    save_data(processed_images, "processed_images.pkl")
                                print(f"processed images are {processed_images}")
                                image.save(f'server_file_{counter}.jpeg', format='JPEG')
                                break
                            # if time.time() - start_time >= timeout:
                            #     print(f"Timeout reached. No message received from worker{get_hostname(received_node_info,worker)}")
                            #     break
            excess_task_queue= remove_processed(original_task_queue, processed_images, original_task_queue.qsize())
            print(f"original task queue size after removing processed images (FOR THE SECOND TIME) is {excess_task_queue.qsize()}")
            
                
        print("All tasks received and processed successfully")
            

        print(f"counter is {counter}")

        break
    print("finished successfully")
    
    

        

else:
                print(f"my rank is {MPI.COMM_WORLD.Get_rank()} and my hostname is {MPI.Get_processor_name()}")

                if MPI.COMM_WORLD.Iprobe(source=0):
                    print("Worker", MPI.COMM_WORLD.Get_rank(), "received task newwww")
                    task_queue = MPI.COMM_WORLD.recv(source=0)
                    print("task received is ", task_queue)
                    WorkerThread(MPI.COMM_WORLD, task_queue).start()
                
                # send rank and hostname to master
                hostname = MPI.Get_processor_name()
                rank = MPI.COMM_WORLD.Get_rank()
                node_info = (rank, hostname)
                MPI.COMM_WORLD.send(node_info, dest=0)
                
                    
                while True:
                        print("Worker", MPI.COMM_WORLD.Get_rank(), "received task")
                        if is_instance_healthy(get_instance_id(MPI.Get_processor_name())):
                            task_queue = MPI.COMM_WORLD.recv(source=0) 
                            if task_queue is None:
                                break
                            else:
                                WorkerThread(MPI.COMM_WORLD, task_queue).start()
                            


                
            
                




          