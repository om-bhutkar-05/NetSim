import socket
import threading

# Constants
ROUTER_IP = "192.168.1.1"
ROUTER_PORT = 10000
CLIENT_EMAIL = "client2@example.com"
CLIENT_IP = "192.168.1.3"
CLIENT_PORT = 10002
INBOX_FILE = "inbox2.txt"
def send_mail(client_socket):
    print("\nSend Mail")
    recipient_email = input("Recipient Email: ")
    subject = input("Subject: ")
    body = input("Message Body: ")

    message = f"MAIL|{recipient_email}|Subject: {subject}\n\n{body}"
    client_socket.send(message.encode("utf-8"))
    print("\nMail Sent!")

def listen_for_mail(client_socket):
    serial_number = 1  # Start with serial number 1

    # Check the current inbox for the highest serial number
    try:
        with open("inbox2.txt", "r") as inbox:
            lines = inbox.readlines()
            for line in lines:
                if line.startswith("#"):
                    last_serial = int(line.split("#")[1].split(":")[0])
                    serial_number = max(serial_number, last_serial + 1)
    except FileNotFoundError:
        pass  # File doesn't exist, start fresh

    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8').strip()
            if message.startswith("MAIL"):
                _, mail_content = message.split('|', 1)
                print(f"\nNew Mail Received:\n{mail_content}")

                # Prepend the mail content to inbox1.txt with a serial number
                new_entry = f"# {serial_number}: {mail_content}\n\n"
                try:
                    with open("inbox2.txt", "r+") as inbox:
                        existing_content = inbox.read()
                        inbox.seek(0)  # Move pointer to the beginning
                        inbox.write(new_entry + existing_content)
                except FileNotFoundError:
                    with open("inbox2.txt", "w") as inbox:
                        inbox.write(new_entry)
                
                serial_number += 1
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

def client_interface():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.bind((CLIENT_IP, CLIENT_PORT))  # Bind to static IP and port
    client_socket.connect((ROUTER_IP, ROUTER_PORT))
    client_socket.send(f"{CLIENT_EMAIL},{CLIENT_IP}".encode("utf-8"))

    while True:
        print("\nWelcome to the Email Client")
        print("1) Send Mail")
        print("2) View Inbox")
        print("3) Visit Website")
        print("4) Quit")
        choice = input("Choose an option (1/2/3/4): ")

        if choice == '1':
            send_mail(client_socket)
        elif choice == '2':
            view_inbox()
        elif choice == '3':
            print("\nVisit Website option selected (to be implemented).")
        elif choice == '4':
            print("\nGoodbye!")
            client_socket.send(b"QUIT")
            client_socket.close()
            break
        else:
            print("\nInvalid choice! Please choose again.")

if __name__ == "__main__":
    client_interface()