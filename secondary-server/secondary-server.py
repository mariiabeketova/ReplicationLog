from flask import Flask, request, jsonify
import os
import requests
import time
import logging

app = Flask(__name__)

# Create an empty list to store received messages
message_list = []

# Secondary server configuration
port = int(os.environ.get('PORT', 5001))
endpoint = os.environ.get('ENDPOINT', 'secondary-server')
registration_interval = int(os.environ.get('REGISTRATION_INTERVAL', 60))  # seconds
service_name = os.environ.get('SERVICE_NAME', 'localhost')

# Register with the master server
master_server_url = os.environ.get('MASTER_SERVER_URL', 'http://localhost:5000')
master_server_rgstr_endpoint = 'register' 

def register_with_master_server():
    while True:
        try:
            response = requests.post(f"{master_server_url}/{master_server_rgstr_endpoint}", json={"url": f"http://{service_name}:{port}/{endpoint}"})
            if response.status_code == 200:
                print(f"Registered with master server at {master_server_url}")
            else:
                print(f"Failed to register with master server. Retrying in {registration_interval} seconds...")
        except requests.exceptions.RequestException:
            print(f"Failed to connect to the master server. Retrying in {registration_interval} seconds...")

        time.sleep(registration_interval)

@app.route(f'/{endpoint}/replicate', methods=['POST'])
def replicate_message():
    logging.info(f"Replication started")
    data = request.json
    message = data.get('message')
    message_list.append(message)
    print(message_list)
    if message:
        # Handle replication logic
        return jsonify({'message_replicated': message})
    else:
        return jsonify({'error': 'Invalid request'}), 400

@app.route(f'/{endpoint}/echo', methods=['GET'])
def get_echo():
    return jsonify({'message_list': message_list})

@app.route(f'/{endpoint}/info', methods=['GET'])
def get_info():
    return jsonify({'message_list': message_list, 'port': port, 'endpoint': endpoint, 'master_server_url': master_server_url})

if __name__ == '__main__':
    # Start the registration process in a separate thread
    import threading
    registration_thread = threading.Thread(target=register_with_master_server)
    registration_thread.daemon = True
    registration_thread.start()

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s')


    app.run(host='0.0.0.0', port=port)