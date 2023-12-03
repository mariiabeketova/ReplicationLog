from quart import Quart, request, jsonify
import os
import requests
import time
import logging
import asyncio
import random
import aiohttp
from aiohttp import ClientSession

app = Quart(__name__)

# Create an empty dictionary to store received messages along with their id's
message_dict = {}
buffer_dict = {}
write_message_lock = asyncio.Lock()

# Secondary server configuration
port = int(os.environ.get('PORT', 5001))
endpoint = os.environ.get('ENDPOINT', 'secondary-server')
registration_interval = int(os.environ.get('REGISTRATION_INTERVAL', 60))  # seconds
service_name = os.environ.get('SERVICE_NAME', 'localhost')

# Master server url
master_server_url = os.environ.get('MASTER_SERVER_URL', 'http://localhost:5000')
master_server_rgstr_endpoint = 'register' 
master_server_echo_endpoint = 'echo' 

# Register with the master server
async def register_with_master_server():

    while True:
        try:
            async with ClientSession() as session:
                async with session.post(f"{master_server_url}/{master_server_rgstr_endpoint}", json={"url": f"http://{service_name}:{port}/{endpoint}"}) as response:
                    if response.status == 200:
                        logging.info(f"Registered with master server at {master_server_url}")
                        return
                    else:
                        logging.error(f"Failed to register with master server. Retrying in {registration_interval} seconds...")
        except aiohttp.ClientError:
            logging.error(f"Failed to connect to the master server. Retrying in {registration_interval} seconds...")

        await asyncio.sleep(registration_interval)


# /replicate POST method
@app.post(f'/{endpoint}/replicate')
async def replicate_message():
    logging.info(f"Replication started")
    data = await request.json#()
    message = data.get('message')
    message_id = int(data.get('id'))
    
    if message:

        # Indroduce the artificial delay on the secondary nodes to emulate replicas inconsistency and test ordering of replicated messages  
        #time.sleep(random.randint(10,20)) 
        await asyncio.sleep(random.randint(10,20))

        # Add the recieved message to a buffer
        buffer_dict[message_id] = message
        logging.info(f"Bufer_dict = {buffer_dict}")
        # Check whether all the previous messages were replicated successfully, if yes - process the next message from the buffer 
        async with write_message_lock:
            for key in sorted(buffer_dict.keys()):
                max_key = max(message_dict.keys()) if message_dict else 0
                if key <= max_key:
                    del buffer_dict[key]
                if key == max_key + 1:
                    message_dict[key] = buffer_dict[key]
                    logging.info(f"Bufer_dict[key] = {buffer_dict[key]}")
                    del buffer_dict[key]
                else:
                    break      

        logging.info(f"message_dict = {message_dict}")

        return jsonify({'message_replicated': message})  # Return a dictionary directly
    else:
        return jsonify({'error': 'Invalid request'}, 400)

# /echo GET method
@app.get(f'/{endpoint}/echo')
async def get_echo():
    return jsonify({'message_list': list(message_dict.values())})



@app.before_serving
async def before_serving():
    asyncio.create_task(register_with_master_server())
    


if __name__ == '__main__':
    
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s')

    app.run(host='0.0.0.0', port=port)