import socket
import threading
import random
import time

# Constants
BUFFER_SIZE = 1024
TIMEOUT_INTERVAL = 2  # Timeout interval in seconds
LOSS_PROBABILITY = 0.1  # Probability of packet loss

# Sender and Receiver Sockets
sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver_socket.bind(("localhost", 12345))

# Sequence Number Tracking
next_sequence_number = 0
acknowledged = set()

# Congestion Control Parameters
cwnd = 1
ssthresh = 16
receiver_window = 5

# Connection Setup

def connection_setup():
    print("Setting up connection...")
    sender_socket.sendto(b"SYN", ("localhost", 12345))
    data, _ = receiver_socket.recvfrom(BUFFER_SIZE)
    if data == b"SYN-ACK":
        sender_socket.sendto(b"ACK", ("localhost", 12345))
    print("Connection established.")

# Connection Teardown

def connection_teardown():
    print("Tearing down connection...")
    sender_socket.sendto(b"FIN", ("localhost", 12345))
    data, _ = receiver_socket.recvfrom(BUFFER_SIZE)
    if data == b"FIN-ACK":
        sender_socket.sendto(b"ACK", ("localhost", 12345))
    print("Connection closed.")

# Reliable Data Transfer - Sender

def rdt_send(data):
    global next_sequence_number, cwnd, ssthresh

    # Split data into packets
    packets = [data[i:i + BUFFER_SIZE] for i in range(0, len(data), BUFFER_SIZE)]
    window_base = 0

    while window_base < len(packets):
        # Send packets in the window
        for i in range(window_base, min(window_base + cwnd, len(packets))):
            if i not in acknowledged:
                # Simulate packet loss
                if random.random() > LOSS_PROBABILITY:
                    packet = f"{next_sequence_number}:{packets[i].decode(errors='ignore')}".encode()
                    sender_socket.sendto(packet, ("localhost", 12345))
                    print(f"Sent packet: {next_sequence_number}")
                else:
                    print(f"Packet {next_sequence_number} lost")
                next_sequence_number += 1

        # Wait for ACKs
        try:
            sender_socket.settimeout(TIMEOUT_INTERVAL)
            ack, _ = sender_socket.recvfrom(BUFFER_SIZE)
            if ":" in ack.decode():
                ack_num = int(ack.decode().split(":")[1])
                print(f"Received ACK: {ack_num}")
                acknowledged.add(ack_num)
                window_base = ack_num + 1

                # Congestion control - AIMD
                if cwnd < ssthresh:
                    cwnd *= 2  # Exponential growth during slow start
                else:
                    cwnd += 1  # Linear growth during congestion avoidance

        except socket.timeout:
            print("Timeout occurred, retransmitting...")
            ssthresh = max(cwnd // 2, 1)
            cwnd = 1  # Reset to slow start

# Reliable Data Transfer - Receiver

def rdt_receive():
    expected_sequence_number = 0
    while True:
        packet, address = receiver_socket.recvfrom(BUFFER_SIZE)
        if ":" in packet.decode():
            sequence_number, data = packet.decode().split(":", 1)
            sequence_number = int(sequence_number)

            if sequence_number == expected_sequence_number:
                print(f"Received packet: {sequence_number}")
                receiver_socket.sendto(f"ACK:{sequence_number}".encode(), address)
                expected_sequence_number += 1
            else:
                # Send ACK for the last correctly received packet
                ack_to_send = expected_sequence_number - 1
                receiver_socket.sendto(f"ACK:{ack_to_send}".encode(), address)

# Start Receiver Thread
receiver_thread = threading.Thread(target=rdt_receive)
receiver_thread.daemon = True
receiver_thread.start()

# Example Usage
if __name__ == "__main__":
    connection_setup()
    rdt_send(b"Hello, this is a test message for the reliable transfer protocol.")
    connection_teardown()
