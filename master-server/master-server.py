from quart import Quart, request, jsonify
import requests
import os
import logging
import time
import asyncio
import aiohttp
from aiohttp import ClientSession
import CountDownLatch

app = Quart(__name__)

message_dict = {} # An empty dictionary to store received messages along with their id's
message_counter = 1
counter_lock = asyncio.Lock()

registered_secondary_servers = set() # Define the URLs of multiple secondary servers

port = int(os.environ.get('PORT', 5000)) # Retrieve configuration from environment variables

#/echo GET method
@app.route('/echo', methods=['GET'])
async def get_echo():
    return jsonify({'message_list': list(message_dict.values())})

#/echo POST method
@app.route('/echo', methods=['POST'])
async def echo_post():
    # Define global variables to use and modify within the async function
    global message_counter

    data = await request.json
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

        result = await replicate_msg(registered_secondary_servers, current_message_id, message, num_to_await)

        if result:
            return jsonify({"status": "success", "data": result})
        else:
            return jsonify({"status": "error", "message": "No successful response"}), 500


#/register POST method
@app.route('/register', methods=['POST'])
async def register_secondary_server():
    data = await request.json
    url = data.get('url')
    if url:
        registered_secondary_servers.add(url)
        logging.info(f"Secondary server ({url}) registered successfully")
        await replicate_all_to_new_secondary(url)
        logging.info(f"Secondary server ({url}) replicated successfully")
        return jsonify({'message': 'Registered successfully'})
    else:
        return jsonify({'error': 'Invalid registration request'}), 400


async def replicate_all_to_new_secondary(secondary_server_url):

    existing_message_dict = message_dict.copy()
    response_status_list = []
    logging.info(f"Secondary server ({secondary_server_url}) replicating all messages")

    # Iterate through each message and replicate to the new secondary server
    for key, value in existing_message_dict.items():
        logging.info(f"Secondary server ({secondary_server_url}) replicating message {value}")
        result = await replicate_msg([secondary_server_url], key, value, 1)
        response_status_list.append(result)

    logging.info(f"Secondary server ({secondary_server_url}) finished replicating messages")

    if response_status_list:
        return jsonify({"status": "success", "data": response_status_list})
    else:
        return jsonify({"status": "error", "message": "No successful response"}), 500


async def replicate_msg(urls, message_id, message, num_to_await):
        
    latch = CountDownLatch.CountDownLatch(num_to_await) # create the countdown latch
    loop = asyncio.get_event_loop()
    for url in urls:
        loop.create_task(post_msg(f"{url}/replicate", message_id, message, latch))
        
    logging.info('Main waiting on latch...')
    await latch.wait()
    logging.info('Main done')


async def post_msg(url, message_id, message, latch, retries=0):
    data = {'id': message_id, 'message': message}
    try:
        async with ClientSession() as session:
            logging.info(f"Sending message to secondary server ({url}) with data = {data}")
            async with session.post(url,json = data) as response:
                if response.status == 200:
                    latch.count_down()
                    logging.info(f'Thread for {url} is done.')
                    return await response.text()
    except Exception as e:
        if retries < 30:
            await asyncio.sleep(1)
            return await post_msg(url, message_id, message, latch, retries + 1)
        else:
            raise e


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s')

    app.run(host='0.0.0.0', port=port)
