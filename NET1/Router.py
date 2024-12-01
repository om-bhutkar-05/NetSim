import socket
import threading

# Constants
ROUTER_IP = "192.168.1.1"
ROUTER_PORT = 10000
MAIL_IPS_FILE = "mail_ips.txt"

# Active client connections
client_connections = {}

def handle_client(client_socket, client_address):
    try:
        # Receive client email and IP
        client_data = client_socket.recv(1024).decode('utf-8').strip()
        client_email, client_ip = client_data.split(',')
        
        print(f"Connected client {client_email} with IP {client_ip}")
        client_connections[client_ip] = client_socket  # Store active connections

        # Save client email and IP to file
        with open(MAIL_IPS_FILE, "a") as file:
            file.write(f"{client_email},{client_ip}\n")

        while True:
            # Receive messages from the client
            message = client_socket.recv(1024).decode('utf-8').strip()
            if message == "QUIT":
                print(f"Client {client_email} with IP {client_ip} disconnected.")
                break

            print(f"Received from {client_ip}: {message}")
            if message.startswith("MAIL"):
                # Extract recipient and message
                _, recipient_email, mail_content = message.split('|', 2)
                route_mail(client_socket, recipient_email, mail_content)
            else:
                client_socket.send(f"Message received: {message}".encode())
    except Exception as e:
        print(f"Error with client {client_address}: {e}")
    finally:
        # Remove client from connections and file on disconnection
        client_connections.pop(client_ip, None)
        with open(MAIL_IPS_FILE, "r") as file:
            lines = file.readlines()
        with open(MAIL_IPS_FILE, "w") as file:
            for line in lines:
                if not line.startswith(client_email):
                    file.write(line)
        client_socket.close()

def route_mail(sender_socket, recipient_email, mail_content):
    try:
        # Find the recipient's IP
        recipient_ip = None
        with open(MAIL_IPS_FILE, "r") as file:
            for line in file:
                email, ip = line.strip().split(',')
                if email == recipient_email:
                    recipient_ip = ip
                    break

        if recipient_ip and recipient_ip in client_connections:
            recipient_socket = client_connections[recipient_ip]
            recipient_socket.send(f"MAIL|{mail_content}".encode('utf-8'))
            sender_socket.send(f"Mail successfully routed to {recipient_email}".encode('utf-8'))
        else:
            sender_socket.send(f"Recipient {recipient_email} not found or offline.".encode('utf-8'))
    except Exception as e:
        print(f"Error routing mail: {e}")
        sender_socket.send("Error routing mail.".encode('utf-8'))

def start_router():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ROUTER_IP, ROUTER_PORT))
    server_socket.listen(5)
    print(f"Router running on {ROUTER_IP}:{ROUTER_PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"New client connected from {client_address}")
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()

if __name__ == "__main__":
    start_router()
