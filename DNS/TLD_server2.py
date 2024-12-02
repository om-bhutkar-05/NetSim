import socket

def handle_request(client_socket):
    domain = client_socket.recv(1024).decode('utf-8')
    print(f"TLD Server 2 received query for domain: {domain}")
    
    # Respond with AS2 IP (for date.in)
    as_ip = "192.168.3.6"
    client_socket.send(as_ip.encode('utf-8'))
    client_socket.close()

def start_tld_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("192.168.3.4", 11002))
    server_socket.listen(5)
    print("TLD Server 2 for .in is running...")

    while True:
        client_socket, _ = server_socket.accept()
        handle_request(client_socket)

if __name__ == "__main__":
    start_tld_server()
