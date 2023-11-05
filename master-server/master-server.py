from flask import Flask, request, jsonify
import requests
import os
import logging
import threading
import time
import asyncio

app = Flask(__name__)

# Create an empty list to store received messages
#message_list = []
# Create an empty dictionary to store received messages along with their id's
message_dict = {}
message_counter = 1
counter_lock = asyncio.Lock()

# Define the URLs of multiple secondary servers
registered_secondary_servers = set()

# Retrieve configuration from environment variables
port = int(os.environ.get('PORT', 5000))

#/echo GET method
@app.route('/echo', methods=['GET'])
async def get_echo():
    return jsonify({'message_list': list(message_dict.values())})

#/echo POST method
@app.route('/echo', methods=['POST'])
async def echo_post():
    # Define global variables to use and modify within the async function
    global message_counter

    data = request.json
    message = data.get('message')
    w = data.get('w') #write concern parameter

    num_to_await = w-1 #number of secondary servers on which data should be replicated before the main process could proceed

    if message:

        async with counter_lock:
            current_message_id = message_counter
            message_dict[current_message_id] = message
            message_counter += 1

        print(message_dict)
        
        # Replicate the message to multiple secondary servers

        # Create a list to store response status codes
        response_status_list = []
        tasks = [] 

        # Start a thread for each secondary server
        for secondary_server_url in registered_secondary_servers:
            task = asyncio.create_task(replicate_message_to_secondary_server(secondary_server_url, current_message_id, message, response_status_list))
            tasks.append(task)

        time.sleep(5)

        # Use asyncio.gather to run all tasks concurrently
        await asyncio.gather(*tasks[:num_to_await])

            
        
        # Check the status codes of all responses
        if all(status_code == 200 for status_code in response_status_list):
            print("All replication tasks were successful (status code 200) as per parameter w")
        else:
            print("Some replication tasks failed")

        time.sleep(5)

        # Print the status codes for reference
        print("Response status codes:", response_status_list)
        
        return jsonify({'echoed_message': message, 'message_list': list(message_dict.values())})
    else:
        return jsonify({'error': 'Invalid request'}), 400

#/register POST method
@app.route('/register', methods=['POST'])
async def register_secondary_server():
    data = request.json
    url = data.get('url')
    if url:
        registered_secondary_servers.add(url)
        logging.info(f"Secondary server ({url}) registered successfully")
        return jsonify({'message': 'Registered successfully'})
    else:
        return jsonify({'error': 'Invalid registration request'}), 400

# Replication to secondaries
async def replicate_message_to_secondary_server(secondary_server_url, message_id, message, response_list):
    logging.info(f"Replication request to secondary server {secondary_server_url} is starting")
    data = {'id':message_id, 'message':message}
    response = requests.post(f'{secondary_server_url}/replicate', json=data)
    response_list.append(response.status_code)
    if response.status_code == 200:
        logging.info(f"Message was replicated successfully to secondary server ({secondary_server_url})")
    else:
        logging.info(f"Failed to replicate message to secondary server ({secondary_server_url}): {response.text}")

if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s')

    app.run(host='0.0.0.0', port=port)
