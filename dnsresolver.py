import socket

# Constants for server IPs and ports
ROOT_NAME_SERVER_IP = "192.168.3.2"
ROOT_NAME_SERVER_PORT = 11000
TLD1_SERVER_IP = "192.168.3.3"
TLD1_SERVER_PORT = 11001
TLD2_SERVER_IP = "192.168.3.4"
TLD2_SERVER_PORT = 11002
AS1_SERVER_IP = "192.168.3.5"
AS1_SERVER_PORT = 11003
AS2_SERVER_IP = "192.168.3.6"
AS2_SERVER_PORT = 11004

def resolve_domain(domain_name):
    # Step 1: Connect to the root name server and get the TLD server IP
    root_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    root_server.connect((ROOT_NAME_SERVER_IP, ROOT_NAME_SERVER_PORT))
    root_server.send(domain_name.encode('utf-8'))
    
    tld_ip = root_server.recv(1024).decode('utf-8')  # TLD1 or TLD2 IP
    print(f"Root Name Server resolved domain to TLD IP: {tld_ip}")
    root_server.close()

    # Step 2: Connect to the TLD server
    if tld_ip == "192.168.3.3":  # TLD1
        tld_server_ip = TLD1_SERVER_IP
        tld_server_port = TLD1_SERVER_PORT
    else:  # TLD2
        tld_server_ip = TLD2_SERVER_IP
        tld_server_port = TLD2_SERVER_PORT

    tld_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tld_server.connect((tld_server_ip, tld_server_port))
    tld_server.send(domain_name.encode('utf-8'))
    
    as_ip = tld_server.recv(1024).decode('utf-8')  # AS1 or AS2 IP
    print(f"TLD Server resolved domain to AS IP: {as_ip}")
    tld_server.close()

    # Step 3: Connect to the AS server
    if as_ip == "192.168.3.5":  # AS1
        as_server_ip = AS1_SERVER_IP
        as_server_port = AS1_SERVER_PORT
    else:  # AS2
        as_server_ip = AS2_SERVER_IP
        as_server_port = AS2_SERVER_PORT

    as_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    as_server.connect((as_server_ip, as_server_port))
    as_server.send(domain_name.encode('utf-8'))
    
    site_ip = as_server.recv(1024).decode('utf-8')  # Final IP
    print(f"AS Server resolved domain to IP: {site_ip}")
    as_server.close()

    return site_ip

def start_dns_resolver():
    # Set up the resolver to listen on 192.168.3.1:11006
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("192.168.3.1", 11006))
    server_socket.listen(5)  # Listen for incoming connections

    print("DNS Resolver is now listening for requests on 192.168.3.1:11006...")
    
    while True:
        # Accept a client connection
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address}")

        try:
            # Receive domain name from the client
            domain_name = client_socket.recv(1024).decode('utf-8')
            print(f"Received domain name: {domain_name}")
            
            # Resolve domain to IP address
            ip_address = resolve_domain(domain_name)
            
            # Send the resolved IP address back to the client
            client_socket.send(ip_address.encode('utf-8'))
            print(f"Sent resolved IP address: {ip_address}")
        
        except Exception as e:
            print(f"Error resolving domain: {e}")
        
        finally:
            client_socket.close()

if __name__ == "__main__":
    start_dns_resolver()
