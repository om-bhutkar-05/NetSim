import socket
import threading
import time

# Constants
ROUTER_IP = "192.168.1.1"
ROUTER_PORT = 10000
CLIENT_EMAIL = "client1@example.com"
CLIENT_IP = "192.168.1.2"
CLIENT_PORT = 10001
INBOX_FILE = "inbox1.txt"
DNS_RESOLVER_IP = "192.168.3.1"  # IP of the DNS resolver
DNS_RESOLVER_PORT = 11006        # Port for the DNS resolver
VALID_WEBSITES = ["time.com", "date.in"]  # Predefined websites
DNS_RESOLVER_TIMEOUT = 5  # Timeout in seconds for DNS resolution

def calculate_checksum(data):
    return sum(ord(char) for char in data) % 256

def verify_checksum(data, checksum):
    return calculate_checksum(data) == checksum

def create_packets(message, subject, source_ip, dest_email):
    packets = []
    lines = message.split('\n')
    for i, line in enumerate(lines, 1):
        checksum = calculate_checksum(line)
        packet = f'PACKET|"{dest_email}"|"{source_ip}"|{i}|"{subject}"|"{line}"|{checksum}'
        packets.append(packet)
    return packets

def send_mail(client_socket):
    print("\nSend Mail")
    recipient_email = input("Recipient Email: ")
    subject = input("Subject: ")
    body = input("Message Body: ")

    packets = create_packets(body, subject, CLIENT_IP, recipient_email)
    for packet in packets:
        client_socket.send(packet.encode("utf-8"))
        print(f"Sending Packet: {packet}")
        time.sleep(0.5)  # Add sleep to simulate packet sending delay

    print("\nMail Sent!")

def listen_for_mail(client_socket):
    inbox = {}
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8').strip()
            if message.startswith("PACKET"):
                
                segments = message.split('|')
                if len(segments) != 7:  
                    print(f"Invalid packet format: {message}")
                    continue

                _, dest_email, source_ip, packet_id, subject, line, checksum = segments
                dest_email = dest_email.strip('"')
                source_ip = source_ip.strip('"')
                subject = subject.strip('"')
                line = line.strip('"')
                packet_id = int(packet_id)
                checksum = int(checksum)

                if verify_checksum(line, checksum):
                    inbox[packet_id] = f"# {packet_id}: Subject: {subject}\n{line}\n"
                    print(f"Packet {packet_id} received and validated.")

                    # Check if all packets are received
                    if len(inbox) == max(inbox.keys()):
                        with open(INBOX_FILE, "a") as file:
                            for i in sorted(inbox.keys()):  # Sorting by packet_id (FIFO)
                                file.write(inbox[i])
                        print("\nMessage successfully assembled and saved.")
                        inbox.clear()
                else:
                    print(f"Packet {packet_id} failed checksum verification.")
        except Exception as e:
            print(f"Error receiving mail: {e}")
            break

def view_inbox():
    print("\n--- Inbox ---")
    try:
        with open(INBOX_FILE, "r") as inbox:
            content = inbox.read()
            if content.strip():
                print(content)
            else:
                print("Your inbox is empty.")
    except FileNotFoundError:
        print("No inbox found! You have no messages yet.")
    print("--- End of Inbox ---")

def resolve_website(website_name):
    """Send a website name to the DNS resolver and get the resolved IP using TCP."""
    if website_name not in VALID_WEBSITES:
        print("Invalid website. Only 'time.com' and 'date.in' are allowed.")
        return None

    try:
        # Use a TCP socket instead of UDP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as dns_socket:
            dns_socket.settimeout(DNS_RESOLVER_TIMEOUT)  # Set timeout for the resolver socket
            dns_socket.connect((DNS_RESOLVER_IP, DNS_RESOLVER_PORT))  # TCP connection to the resolver
            dns_socket.send(website_name.encode())  # Send the website name
            resolved_ip = dns_socket.recv(1024).decode()  # Receive the resolved IP
            print(f"Resolved IP for {website_name}: {resolved_ip}")
            return resolved_ip
    except socket.timeout:
        print(f"Error: DNS resolver timed out while resolving {website_name}.")
        return None
    except Exception as e:
        print(f"Error resolving website {website_name}: {e}")
        return None


def connect_to_website(ip):
    """Connect to the resolved website IP and receive a response."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as web_socket:
            web_socket.connect((ip, 8080))  # Assuming port 8080 for web servers
            response = web_socket.recv(1024).decode()
        return response
    except Exception as e:
        print(f"Error connecting to website: {e}")
        return None

def client_interface():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.bind((CLIENT_IP, CLIENT_PORT))
    client_socket.connect((ROUTER_IP, ROUTER_PORT))
    client_socket.send(f"{CLIENT_EMAIL},{CLIENT_IP}".encode("utf-8"))

    threading.Thread(target=listen_for_mail, args=(client_socket,), daemon=True).start()

    while True:
        print("\nWelcome to the Email Client")
        print("1) Send Mail")
        print("2) View Inbox")
        print("3) Visit Website (time.com / date.in)")
        print("4) Quit")
        choice = input("Choose an option (1/2/3/4): ")

        if choice == '1':
            send_mail(client_socket)
        elif choice == '2':
            view_inbox()
        elif choice == '3':
            website_name = input("Enter website name (time.in or date.in): ")
            ip = resolve_website(website_name)
            if ip:
                print(f"Resolved IP for {website_name}: {ip}")
                response = connect_to_website(ip)
                if response:
                    print(f"Website Response: {response}")
                else:
                    print("Failed to receive a response from the website.")
        elif choice == '4':
            print("\nGoodbye!")
            client_socket.send(b"QUIT")
            client_socket.close()
            break
        else:
            print("\nInvalid choice! Please choose again.")

if __name__ == "__main__":
    client_interface()
