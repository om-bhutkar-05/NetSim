import socket

def send_mail(client_socket, client_email, client_port):
    print("\nSend Mail")
    recipient_email = input("Recipient Email: ")
    subject = input("Subject: ")
    body = input("Message Body: ")

    message = f"From: {client_email}\nTo: {recipient_email}\nSubject: {subject}\n\n{body}"
    client_socket.send(message.encode("utf-8"))
    print("\nMail Sent!")

def client_interface():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('192.168.1.1', 9999))

    client_email = "client@example.com"
    client_port = client_socket.getsockname()[1]
    client_socket.send(f"{client_email},{client_port}".encode('utf-8'))
    
    while True:
        print("\nWelcome to the Email Client")
        print("1) Send Mail")
        print("2) Visit Website (Empty for now)")
        print("3) Quit")
        choice = input("Choose an option (1/2/3): ")

        if choice == '1':
            print("\nConnecting to Router...")
            send_mail(client_socket, client_email, client_port)

        elif choice == '2':
            print("\nVisit Website feature is not yet implemented.")
        
        elif choice == '3':
            print("\nGoodbye!")
            client_socket.close()
            break
        else:
            print("\nInvalid choice! Please choose a valid option.")

if __name__ == '__main__':
    client_interface()
