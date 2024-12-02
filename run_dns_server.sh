#!/bin/bash

# Start root name server
echo "Starting Root Name Server..."
python3 DNS/root_name_server.py &
sleep 2  # Giving time for the server to start

# Start TLD Server 1
echo "Starting TLD Server 1..."
python3 DNS/TLD_server1.py &
sleep 2  # Giving time for the server to start

# Start TLD Server 2
echo "Starting TLD Server 2..."
python3 DNS/TLD_server2.py &
sleep 2  # Giving time for the server to start

# Start AS Server 1
echo "Starting AS Server 1..."
python3 DNS/AS1.py &
sleep 2  # Giving time for the server to start

# Start AS Server 2
echo "Starting AS Server 2..."
python3 DNS/AS2.py &
sleep 2  # Giving time for the server to start


# Optionally, you can also start the other services (like time and date servers)
echo "Starting Date and Time Servers..."
python3 DNS/date.py &
python3 DNS/time.py &
