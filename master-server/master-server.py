from flask import Flask, request, jsonify
import requests
import os
import logging
import threading
import time

app = Flask(__name__)

# Create an empty list to store received messages
message_list = []

# Define the URLs of multiple secondary servers
registered_secondary_servers = set()

# Retrieve configuration from environment variables
port = int(os.environ.get('PORT', 5000))

#/echo GET method
@app.route('/echo', methods=['GET'])
def get_echo():
    return jsonify({'message_list': message_list})

#/echo POST method
@app.route('/echo', methods=['POST'])
def echo_post():
    data = request.json
    message = data.get('message')
    if message:
        message_list.append(message)
        print(message_list)
        
        # Replicate the message to multiple secondary servers

        # Create a list to hold thread objects
        threads = []

        # Create a list to store response status codes
        response_status_list = []

        # Start a thread for each secondary server
        for secondary_server_url in registered_secondary_servers:
            thread = threading.Thread(target=replicate_message_to_secondary_server, args=(secondary_server_url, message, response_status_list))
            thread.start()
            threads.append(thread)

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check the status codes of all responses
        if all(status_code == 200 for status_code in response_status_list):
            print("All replication tasks were successful (status code 200)")
        else:
            print("Some replication tasks failed")

        time.sleep(5)

        # Print the status codes for reference
        print("Response status codes:", response_status_list)
        
        return jsonify({'echoed_message': message, 'message_list': message_list})
    else:
        return jsonify({'error': 'Invalid request'}), 400

#/register POST method
@app.route('/register', methods=['POST'])
def register_secondary_server():
    data = request.json
    url = data.get('url')
    if url:
        registered_secondary_servers.add(url)
        logging.info(f"Secondary server ({url}) registered successfully")
        return jsonify({'message': 'Registered successfully'})
    else:
        return jsonify({'error': 'Invalid registration request'}), 400

@app.route(f'/info', methods=['GET'])
def get_info():
    return jsonify({'message_list': message_list, 'port': port, 'registered_secondary_servers': list(registered_secondary_servers)})

def replicate_message_to_secondary_server(secondary_server_url, message, response_list):
    # Send a POST request to a secondary server to replicate the message
    logging.info(f"Replication request to secondary server {secondary_server_url} is starting")
    data = {'message': message}
    response = requests.post(f'{secondary_server_url}/replicate', json=data)
    response_list.append(response.status_code)
    if response.status_code == 200:
        logging.info(f"Message was replicated successfully to secondary server ({secondary_server_url})")
    else:
        logging.info(f"Failed to replicate message to secondary server ({secondary_server_url}): {response.text}")

if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s')

    app.run(host='0.0.0.0', port=port)
