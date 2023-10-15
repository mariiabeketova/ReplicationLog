import requests
import os

master_server_url = os.environ.get('MASTER_SERVER_URL', 'http://localhost:5000')
master_server_echo_endpoint = 'echo'
secondary_server1_url = 'http://localhost:5001'
secondary_server2_url = 'http://localhost:5002'
secondary_server3_url = 'http://localhost:5003'
secondary_server1_echo_endpoint = '/server1/echo'
secondary_server1_info_endpoint = '/server1/info'
secondary_server2_echo_endpoint = '/server2/echo'
secondary_server2_info_endpoint = '/server2/info'
secondary_server3_echo_endpoint = '/server3/echo'
secondary_server3_info_endpoint = '/server3/info'


def get_echo(url):
    response = requests.get(url)
    return response.json()

def post_echo(url, message):
    data = {'message': message}
    response = requests.post(url, json=data)
    return response.json()

if __name__ == '__main__':
    while True:
        print("Choose an action:")
        print("a. Send GET request(master)")
        print("b. Send POST request(master)")
        print("c. Send GET request(secondary1)")
        print("d. Send INFO request(secondary1)")
        print("e. Send GET request(secondary2)")
        print("f. Send INFO request(secondary2)")
        print("g. Send GET request(secondary3)")
        print("h. Send INFO request(secondary3)")
        print("i. Send INFO request(master)")
        print("j. Quit")
        
        choice = input("Enter your choice: ")
        
        if choice == 'a':
            response = get_echo(f"{master_server_url}/{master_server_echo_endpoint}")
            print(f"Server response (GET): {response['message_list']}")
        elif choice == 'b':
            message = input("Enter a message to send: ")
            response = post_echo(f"{master_server_url}/{master_server_echo_endpoint}", message)
            print(f"Server response (POST - Echoed Message): {response.get('echoed_message', 'No echoed message received')}")
        elif choice == 'c':
            response = get_echo(f"{secondary_server1_url}/{secondary_server1_echo_endpoint}")
            print(f"Server response (GET): {response['message_list']}")
        elif choice == 'd':
            response = get_echo(f"{secondary_server1_url}/{secondary_server1_info_endpoint}")
            print(f"Server response (GET): {response['message_list']}, {response['port']}, {response['endpoint']}, {response['master_server_url']}")
        elif choice == 'e':
            response = get_echo(f"{secondary_server2_url}/{secondary_server2_echo_endpoint}")
            print(f"Server response (GET): {response['message_list']}")
        elif choice == 'f':
            response = get_echo(f"{secondary_server2_url}/{secondary_server2_info_endpoint}")
            print(f"Server response (GET): {response['message_list']}, {response['port']}, {response['endpoint']}, {response['master_server_url']}")
        elif choice == 'g':
            response = get_echo(f"{secondary_server3_url}/{secondary_server3_echo_endpoint}")
            print(f"Server response (GET): {response['message_list']}")
        elif choice == 'h':
            response = get_echo(f"{secondary_server3_url}/{secondary_server3_info_endpoint}")
            print(f"Server response (GET): {response['message_list']}, {response['port']}, {response['endpoint']}, {response['master_server_url']}")
        elif choice == 'i':
            response = get_echo(f"{master_server_url}/info")
            print(f"Server response (GET): {response['message_list']}, {response['port']}, {response['registered_secondary_servers']}")
        elif choice == 'j':
            break
        else:
            print("Invalid choice. Please try again.")