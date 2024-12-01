import socket
import threading
import random
import time

router_ip = "192.168.1.1"
subnet = "192.168.1.0/24"
available_ips = [f"192.168.1.{i}" for i in range(2, 7)]

mail_ips_file = "mail_ips.txt"

def assign_ip():
    if available_ips:
        return available_ips.pop(0)
    else:
        return None

def handle_client(client_socket, client_address):
    assigned_ip = assign_ip()
    if assigned_ip:
        print(f"Assigned IP {assigned_ip} to client {client_address}")
        with open(mail_ips_file, "a") as file:
            file.write(f"{assigned_ip}\n")
        client_socket.send(f"Your assigned IP is {assigned_ip}".encode())
        
        while True:
            message = client_socket.recv(1024)
            if not message:
                break
            print(f"Received message from {assigned_ip}: {message.decode()}")
            client_socket.send(f"Message received: {message.decode()}".encode())
    else:
        print(f"No available IP for client {client_address}")
        client_socket.send(b"No available IP. Try again later.")

    if assigned_ip:
        with open(mail_ips_file, "r") as file:
            lines = file.readlines()
        with open(mail_ips_file, "w") as file:
            for line in lines:
                if line.strip() != assigned_ip:
                    file.write(line)
        available_ips.append(assigned_ip)

    client_socket.close()

def start_router():
    server_ip = router_ip
    server_port = 9999
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(5)
    print(f"Router1 is running on {server_ip}:{server_port}...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"New client connected from {client_address}")
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    start_router()
