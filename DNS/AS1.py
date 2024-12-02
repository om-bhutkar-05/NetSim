import socket

def handle_request(client_socket):
    domain = client_socket.recv(1024).decode('utf-8')
    print(f"AS Server 1 received query for domain: {domain}")
    
    # Respond with the actual IP of time.com
    site_ip = "192.168.1.4"  # IP for time.com
    client_socket.send(site_ip.encode('utf-8'))
    client_socket.close()

def start_as_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("192.168.3.5", 11003))
    server_socket.listen(5)
    print("AS Server 1 for time.com is running...")

    while True:
        client_socket, _ = server_socket.accept()
        handle_request(client_socket)

if __name__ == "__main__":
    start_as_server()
