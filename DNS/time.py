import socket
from datetime import datetime

def start_time_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("192.168.1.4", 8080))  # IP and port for time.com
    server_socket.listen(5)
    print("Time Server is running...")

    while True:
        client_socket, _ = server_socket.accept()
        print("Client connected to Time Server.")

        # Send the current time to the client
        current_time = datetime.now().strftime("%H:%M:%S")
        client_socket.send(current_time.encode('utf-8'))

        client_socket.close()

if __name__ == "__main__":
    start_time_server()
