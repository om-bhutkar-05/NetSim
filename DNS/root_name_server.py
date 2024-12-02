import socket

def handle_request(client_socket):
    domain = client_socket.recv(1024).decode('utf-8')
    print(f"Root Server received query for domain: {domain}")
    
    if domain.endswith(".com"):
        tld_ip = "192.168.3.3"  # TLD server for .com
    elif domain.endswith(".in"):
        tld_ip = "192.168.3.4"  # TLD server for .in
    else:
        tld_ip = "Unknown domain"
    
    client_socket.send(tld_ip.encode('utf-8'))
    client_socket.close()

def start_root_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("192.168.3.2", 11000))
    server_socket.listen(5)
    print("Root Name Server is running...")

    while True:
        client_socket, _ = server_socket.accept()
        handle_request(client_socket)

if __name__ == "__main__":
    start_root_server()
