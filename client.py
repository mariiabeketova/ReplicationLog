import requests
import os

master_server_url = os.environ.get('MASTER_SERVER_URL', 'http://localhost:5000')
master_server_echo_endpoint = 'echo'
secondary_server1_url = 'http://localhost:5001'
secondary_server2_url = 'http://localhost:5002'
secondary_server3_url = 'http://localhost:5003'
secondary_server1_echo_endpoint = 'server1/echo' #'secondary-server/echo' #
secondary_server2_echo_endpoint = 'server2/echo' #'secondary-server2/echo' #
secondary_server3_echo_endpoint = 'server3/echo' #'secondary-server3/echo' #


def get_echo(url):
    response = requests.get(url)
    return response.json()

def post_echo(url, data):
    response = requests.post(url, json=data)
    return response.json()

if __name__ == '__main__':
    while True:
        print("Choose an action:")
        print("a. Send GET request(master)")
        print("b. Send POST request(master)")
        print("c. Send GET request(secondary1)")
        print("d. Send GET request(secondary2)")
        print("e. Send GET request(secondary3)")
        print("f. Quit")
        
        choice = input("Enter your choice: ")
        
        if choice == 'a':
            response = get_echo(f"{master_server_url}/{master_server_echo_endpoint}")
            print(f"Server response (GET): {response['message_list']}")
        elif choice == 'b':
            message = input("Enter a message to send: ")
            w = int(input("Enter 'write concern parameter' (w=1,2..n): "))
            data = {'message': message, 'w': w}
            response = post_echo(f"{master_server_url}/{master_server_echo_endpoint}", data)
            print(f"Server response (POST - Echoed Message): {response.get('echoed_message', 'No echoed message received')}")
        elif choice == 'c':
            response = get_echo(f"{secondary_server1_url}/{secondary_server1_echo_endpoint}")
            print(f"Server response (GET): {response['message_list']}")
        elif choice == 'd':
            response = get_echo(f"{secondary_server2_url}/{secondary_server2_echo_endpoint}")
            print(f"Server response (GET): {response['message_list']}")
        elif choice == 'e':
            response = get_echo(f"{secondary_server3_url}/{secondary_server3_echo_endpoint}")
            print(f"Server response (GET): {response['message_list']}")
        elif choice == 'f':
            break
        else:
            print("Invalid choice. Please try again.")