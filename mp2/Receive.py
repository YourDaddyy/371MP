import socket
import threading
import random
import time

# Constants
BUFFER_SIZE = 1024


# Sender and Receiver Sockets
receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver_socket.bind(("localhost", 12345))


# Congestion Control Parameters
receiver_window = 5


def rdt_receive():
    expected_sequence_number = 0
    receiver_buffer = []  # Simulate a buffer to hold incoming data packets
    while True:
        packet, address = receiver_socket.recvfrom(BUFFER_SIZE)
        if ":" in packet.decode():
            sequence_number, data = packet.decode().split(":", 1)
            sequence_number = int(sequence_number)

            if sequence_number == expected_sequence_number:
                print(f"Receiver: Received packet: {sequence_number}")
                receiver_buffer.append(data)
                receiver_socket.sendto(f"ACK:{sequence_number}".encode(), address)
                expected_sequence_number += 1

            else:
                # Send ACK for the last correctly received packet
                ack_to_send = expected_sequence_number - 1
                receiver_socket.sendto(f"ACK:{ack_to_send}".encode(), address)

        elif packet == b"FIN":
            print("Receiver: connection teardown initiated by sender.")
            receiver_socket.sendto(b"FIN-ACK", address)
            print("Receiver: connection closed.")
            break

# Start receiver to keep listening
def start_receive():
    print("Receiver: Waiting for connection...")
    while True:  # Keep listening for connection setup and data
        data, sender_address = receiver_socket.recvfrom(BUFFER_SIZE)
        if data == b"SYN":
            print("Receiver: Received SYN, sending SYN-ACK...")
            receiver_socket.sendto(b"SYN-ACK", sender_address)
            data, _ = receiver_socket.recvfrom(BUFFER_SIZE)
            if data == b"ACK":
                print("Receiver: Connection established.")
                rdt_receive()

# Example Usage
if __name__ == "__main__":
    start_receive()
