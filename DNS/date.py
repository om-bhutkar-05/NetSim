import socket
from datetime import datetime

def start_date_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("192.168.1.5", 8080))  # IP and port for date.in
    server_socket.listen(5)
    print("Date Server is running...")

    while True:
        client_socket, _ = server_socket.accept()
        print("Client connected to Date Server.")

        # Send the current date to the client
        current_date = datetime.now().strftime("%Y-%m-%d")
        client_socket.send(current_date.encode('utf-8'))

        client_socket.close()

if __name__ == "__main__":
    start_date_server()
