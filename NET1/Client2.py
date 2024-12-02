import socket
import threading
import time
from colorama import Fore, Style
import pyfiglet
from alive_progress import alive_bar

# Constants
ROUTER_IP = "192.168.1.1"
ROUTER_PORT = 10000
CLIENT_EMAIL = "client2@example.com"
CLIENT_IP = "192.168.1.3"
CLIENT_PORT = 10002
INBOX_FILE = "inbox2.txt"
DNS_RESOLVER_IP = "192.168.3.1"  # IP of the DNS resolver
DNS_RESOLVER_PORT = 11006        # Port for the DNS resolver
VALID_WEBSITES = ["time.com", "date.in"]  # Predefined websites
DNS_RESOLVER_TIMEOUT = 5  # Timeout in seconds for DNS resolution

def animated_menu():
    print(Fore.CYAN + pyfiglet.figlet_format("Network Simulator") + Style.RESET_ALL)
    for i in range(3):
        print(f"{Fore.MAGENTA}Loading Menu{'.' * (i+1)}{Style.RESET_ALL}")
        time.sleep(0.5)

def colorful_menu():
    print(Fore.YELLOW + "***************************************")
    print("* Welcome to the Enhanced Email Client *")
    print("***************************************" + Style.RESET_ALL)
    print(Fore.GREEN + "1) Send Mail")
    print("2) View Inbox")
    print("3) Visit Website (time.com / date.in)")
    print("4) Quit" + Style.RESET_ALL)

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
    print(Fore.CYAN + Style.BRIGHT + "\nSend Mail" + Style.RESET_ALL)
    recipient_email = input(Fore.GREEN + "Recipient Email: " + Style.RESET_ALL)
    subject = input(Fore.GREEN + "Subject: " + Style.RESET_ALL)

    print(Fore.YELLOW + "\nEnter your message (type 'END' on a new line to finish):" + Style.RESET_ALL)
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)
    body = "\n".join(lines)

    # Confirming the message
    print(Fore.MAGENTA + "\nMessage composed:" + Style.RESET_ALL)
    print(Fore.WHITE + body + Style.RESET_ALL)

    # Create and send packets
    packets = create_packets(body, subject, CLIENT_IP, recipient_email)
    with alive_bar(len(packets), title="Sending Packets") as bar:
        for i, packet in enumerate(packets, start=1):
            print(Fore.BLUE + f"Sending Packet {i}: " + Fore.WHITE + packet + Style.RESET_ALL)
            client_socket.send(packet.encode("utf-8"))
            bar()
            time.sleep(0.5)  # Simulate a realistic delay for packet sending

    print(Fore.GREEN + Style.BRIGHT + "\nMail Sent Successfully!" + Style.RESET_ALL)


def listen_for_mail(client_socket):
    received_packets = {}  # Store packets by packet_id
    current_subject = None  # Store the current subject of the message
    message_lines = []      # Accumulate message lines here
    message_counter = 1     # To track serial numbers for messages

    print(Fore.CYAN + "\nReceiving Mail..." + Style.RESET_ALL)
    
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8').strip()

            # Split multiple packets if they are concatenated together
            packets = message.split("PACKET|")[1:]  # Split by 'PACKET|' and ignore the first empty result

            for packet in packets:
                packet = "PACKET|" + packet  # Add back the "PACKET|" to each packet
                segments = packet.split('|')

                if len(segments) != 7:
                    print(Fore.RED + f"Invalid packet format: {packet}" + Style.RESET_ALL)
                    continue

                try:
                    _, dest_email, source_ip, packet_id, subject_line, line, checksum = segments
                    subject_line = subject_line.strip('"')
                    line = line.strip('"')
                    packet_id = int(packet_id)
                    checksum = int(checksum)

                    print(Fore.YELLOW + f"\nPacket {packet_id} from {source_ip} with Subject: {subject_line}" + Style.RESET_ALL)
                    print(f"Line: {line}")
                    print(f"Checksum for this line: {checksum}")
                    if verify_checksum(line, checksum):
                        print(Fore.GREEN + f"Packet {packet_id} received and validated successfully." + Style.RESET_ALL)

                        # Initialize subject when the first packet is received
                        if current_subject is None:
                            current_subject = subject_line

                        # Store packet in the received packets buffer
                        received_packets[packet_id] = line

                    # Check for "end of message" signal (could be a special packet or message format)
                    if "FIN" in line:
                        print(Fore.CYAN + "End of message detected! Assembling message..." + Style.RESET_ALL)
                        
                        # Assemble the message by sorting the packets by packet_id
                        for packet_id in sorted(received_packets.keys()):
                            message_lines.append(received_packets[packet_id])

                        # Add serial number to the message
                        print(Fore.CYAN + f"\nSaving message {message_counter} to inbox..." + Style.RESET_ALL)
                        save_message_to_inbox(current_subject, message_lines, message_counter)

                        # Reset variables for the next message
                        received_packets.clear()
                        message_lines.clear()
                        current_subject = None
                        message_counter += 1

                except ValueError as e:
                    print(Fore.RED + f"Error parsing packet fields: {e}" + Style.RESET_ALL)

        except Exception as e:
            print(Fore.RED + f"Error receiving mail: {e}" + Style.RESET_ALL)
            break

def save_message_to_inbox(subject, message_lines, message_number):
    # Save the subject and the full message lines to the inbox file
    with open(INBOX_FILE, "a") as file:
        file.write(f"Message {message_number}:\n")
        file.write(f"Subject: {subject}\n")
        for line in message_lines:
            file.write(f"{line}\n")

    # Display a progress bar while saving the message
    with alive_bar(len(message_lines), title=f"Saving message {message_number}") as bar:
        for _ in message_lines:
            bar()

    print(Fore.GREEN + "Message successfully saved to inbox." + Style.RESET_ALL)
    
def view_inbox():
    print(Fore.YELLOW + "\n--- Inbox ---" + Style.RESET_ALL)
    try:
        with open(INBOX_FILE, "r") as inbox:
            content = inbox.read()
            if content.strip():
                print(content)
            else:
                print(Fore.CYAN + "Your inbox is empty." + Style.RESET_ALL)
    except FileNotFoundError:
        print(Fore.RED + "No inbox found! You have no messages yet." + Style.RESET_ALL)
    print(Fore.YELLOW + "--- End of Inbox ---" + Style.RESET_ALL)

def resolve_website(website_name):
    if website_name not in VALID_WEBSITES:
        print(Fore.RED + "Invalid website. Only 'time.com' and 'date.in' are allowed." + Style.RESET_ALL)
        return None

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as dns_socket:
            dns_socket.settimeout(DNS_RESOLVER_TIMEOUT)
            dns_socket.connect((DNS_RESOLVER_IP, DNS_RESOLVER_PORT))
            dns_socket.send(website_name.encode())
            resolved_ip = dns_socket.recv(1024).decode()
            print(Fore.MAGENTA + f"Resolved IP for {website_name}: {resolved_ip}" + Style.RESET_ALL)
            return resolved_ip
    except socket.timeout:
        print(Fore.RED + f"Error: DNS resolver timed out while resolving {website_name}." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Error resolving website {website_name}: {e}" + Style.RESET_ALL)
    return None

def connect_to_website(ip):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as web_socket:
            web_socket.connect((ip, 8080))
            response = web_socket.recv(1024).decode()
        return response
    except Exception as e:
        print(Fore.RED + f"Error connecting to website: {e}" + Style.RESET_ALL)
        return None

def client_interface():
    animated_menu()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.bind((CLIENT_IP, CLIENT_PORT))
    client_socket.connect((ROUTER_IP, ROUTER_PORT))
    client_socket.send(f"{CLIENT_EMAIL},{CLIENT_IP}".encode("utf-8"))

    threading.Thread(target=listen_for_mail, args=(client_socket,), daemon=True).start()

    while True:
        colorful_menu()
        choice = input(Fore.BLUE + "Choose an option (1/2/3/4): " + Style.RESET_ALL)

        if choice == '1':
            send_mail(client_socket)
        elif choice == '2':
            view_inbox()
        elif choice == '3':
            website_name = input(Fore.CYAN + "Enter website name (time.com or date.in): " + Style.RESET_ALL)
            ip = resolve_website(website_name)
            if ip:
                response = connect_to_website(ip)
                if response:
                    print(Fore.MAGENTA + f"Website Response: {response}" + Style.RESET_ALL)
                else:
                    print(Fore.RED + "Failed to receive a response from the website." + Style.RESET_ALL)
        elif choice == '4':
            print(Fore.RED + "\nGoodbye!" + Style.RESET_ALL)
            client_socket.send(b"QUIT")
            client_socket.close()
            break
        else:
            print(Fore.RED + "\nInvalid choice! Please choose again." + Style.RESET_ALL)

if __name__ == "__main__":
    client_interface()
