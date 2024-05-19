""""
This file contains the functions to start and stop the EC2 instances.
It also contains the functions to check the health of the instances.
The instances are identified by their instance IDs.
The instance IDs are stored in a dictionary with the hostname as the key.
The instance IDs are used to start and stop the instances.
The hostname is used to identify the instance that is alive.
The function check_if_any_alive() returns True if any instance is alive.
The function get_instance_id() returns the instance ID for a given hostname.
The function is_instance_healthy() checks if the instance is healthy.
The function start_instance() starts the instance with the given instance ID.

<<<<<<<<<<<
Note: The AWS credentials are hardcoded in the code.
You can replace them with your own credentials.


and we cannot show our instance id  and address in the code so we have to replace them with the addresssss and id
<<<<<<<<<<<


"""

import boto3
import time
instance_ids= {"slave1":"addreeesssssssssss", 
               "slave2":"addreeesssssssssss", 

                "and so on": "addreeesssssssssss"
            }
def is_instance_healthy(instance_id):
    
    try:
        ec2_client = boto3.client('ec2', region_name='eu-north-1', aws_access_key_id='aws_access_key_id',
                                  aws_secret_access_key= "aws_secret_access_key")
        
        response = ec2_client.describe_instance_status(InstanceIds=[instance_id])

        if len(response['InstanceStatuses']) > 0:
            instance_status = response['InstanceStatuses'][0]['InstanceState']['Name']
            return instance_status == 'running'
        else:
            return False
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return False 

def get_instance_id(hostname):
    """"
    This function returns the instance ID for a given hostname.
    The instance IDs are stored in a dictionary with the hostname as the key.
    The function returns the instance ID for the given hostname.
    If the hostname is not found in the dictionary, it prints an error message and returns None.
    """
    if hostname == "slave1":
        return "addreesssssssssss"

    else:
        print(f"Instance ID for {hostname} not found")
        return None
    
def stop_instance(instance_id):
    ec2_client = boto3.client('ec2', region_name='eu-north-1', aws_access_key_id='aws_access_key_id',
                                  aws_secret_access_key= "secret_key")
    ec2_client.stop_instances(InstanceIds=[instance_id])
    print(f"Instance {instance_id} stopped successfully")

def start_instance(instance_id):
    ec2_client = boto3.client('ec2', region_name='eu-north-1', aws_access_key_id='aws_access_key_id',
                                  aws_secret_access_key= "secret_key")  
    try:   
        time.sleep(30)
        # instance_id= instance_ids['slave1']
        ec2_client.start_instances(InstanceIds=[instance_id])
        print("Starting instance", instance_id)
        waiter = ec2_client.get_waiter('instance_running')
        waiter.wait(InstanceIds=[instance_id])
        print("Instance", instance_id, "is now running")
        return True
    except Exception as e:
        return False
    
def check_if_any_alive():
    for hostname, instance_id in instance_ids.items():
        if is_instance_healthy(instance_id):
            return True, hostname
    return False, None