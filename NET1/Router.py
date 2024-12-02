import socket
import threading
import time

# Constants
ROUTER_IP = "192.168.1.1"
ROUTER_PORT = 10000
MAIL_IPS_FILE = "mail_ips.txt"

# Active client connections
client_connections = {}
server_socket = None

def cleanup():
    """Cleanup function to close all client connections and the server socket."""
    print("Cleaning up...")
    for client_socket in client_connections.values():
        try:
            client_socket.close()
        except Exception as e:
            print(f"Error closing client socket: {e}")
    if server_socket:
        try:
            server_socket.close()
        except Exception as e:
            print(f"Error closing server socket: {e}")

def handle_client(client_socket, client_address):
    try:
        client_data = client_socket.recv(1024).decode('utf-8').strip()
        client_email, client_ip = client_data.split(',')
        print(f"Connected client {client_email} with IP {client_ip}")
        client_connections[client_ip] = client_socket

        with open(MAIL_IPS_FILE, "a") as file:
            file.write(f"{client_email},{client_ip}\n")

        while True:
            message = client_socket.recv(1024).decode('utf-8').strip()
            if message == "QUIT":
                print(f"Client {client_email} disconnected.")
                break

            if message.startswith("PACKET"):
                forward_packet(message)
    except Exception as e:
        print(f"Error with client {client_address}: {e}")
    finally:
        client_connections.pop(client_ip, None)
        with open(MAIL_IPS_FILE, "r") as file:
            lines = file.readlines()
        with open(MAIL_IPS_FILE, "w") as file:
            for line in lines:
                if not line.startswith(client_email):
                    file.write(line)
        client_socket.close()

def forward_packet(packet):
    try:
        _, dest_email, content = packet.split('|', 2)
        recipient_ip = None
        print(f"Routing packet to: {dest_email}")
        with open(MAIL_IPS_FILE, "r") as file:
            for line in file:
                if line.strip():
                    email, ip = line.strip().split(',')
                    print(email,dest_email)
                    if email[0:19] == dest_email[1:20]:
                        recipient_ip = ip
                        break
        
        if recipient_ip and recipient_ip in client_connections:
            print(f"Forwarding packet to {recipient_ip}...")
            time.sleep(2.5)  # Simulating the forwarding delay
            client_connections[recipient_ip].send(packet.encode('utf-8'))
            print(f"Packet forwarded to {dest_email}")
        else:
            print(f"Recipient {dest_email} not found or offline.")
    except Exception as e:
        print(f"Error forwarding packet: {e}")

def start_router():
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ROUTER_IP, ROUTER_PORT))
    server_socket.listen(5)
    print(f"Router running on {ROUTER_IP}:{ROUTER_PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()

if __name__ == "__main__":
    start_router()
