import socket
import threading
import random
import time

# Constants
BUFFER_SIZE = 1024
TIMEOUT_INTERVAL = 2  # Timeout interval in seconds
LOSS_PROBABILITY = 0.9  # Probability of packet loss
RECEIVER_ADDRESS = ("localhost", 12345)

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

# def connection_setup():
#     print("Setting up connection...")
#     sender_socket.sendto(b"SYN", ("localhost", 12345))
#     data, _ = receiver_socket.recvfrom(BUFFER_SIZE)
#     if data == b"SYN-ACK":
#         sender_socket.sendto(b"ACK", ("localhost", 12345))
#     print("Connection established.")

# # Connection Teardown

# def connection_teardown():
#     print("Tearing down connection...")
#     sender_socket.sendto(b"FIN", ("localhost", 12345))
#     data, _ = receiver_socket.recvfrom(BUFFER_SIZE)
#     if data == b"FIN-ACK":
#         sender_socket.sendto(b"ACK", ("localhost", 12345))
#     print("Connection closed.")

# Reliable Data Transfer - Sender

def rdt_send(data):
    global next_sequence_number, cwnd, ssthresh

    # Split data into packets
    packets = [data[i:i + BUFFER_SIZE] for i in range(0, len(data), BUFFER_SIZE)]
    window_base = 0

    while window_base < len(packets):
        # Send packets in the window
        # for i in range(window_base, min(window_base + cwnd, len(packets))):
        #     if i not in acknowledged:
        #         # Simulate packet loss
        #         if random.random() > LOSS_PROBABILITY:
        #             packet = f"{next_sequence_number}:{packets[i].decode(errors='ignore')}".encode()
        #             sender_socket.sendto(packet, ("localhost", 12345))
        #             print(f"Sender: Sent packet: {next_sequence_number}")
        #         else:
        #             print(f"Sender: Packet {next_sequence_number} lost")
        #         next_sequence_number += 1
        
        for i in range(window_base, min(window_base + cwnd, len(packets))):
            if i not in acknowledged:
                # Simulate packet loss
                if random.random() > LOSS_PROBABILITY:
                    packet = f"{i}:{packets[i].decode(errors='ignore')}".encode()
                    sender_socket.sendto(packet, ("localhost", 12345))
                    print(f"Sender: Sent packet: {i}")
                else:
                    print(f"Sender: Packet {i} lost")

        # Wait for ACKs
        try:
            sender_socket.settimeout(TIMEOUT_INTERVAL)
            ack, _ = sender_socket.recvfrom(BUFFER_SIZE)
            if ":" in ack.decode():
                ack_num = int(ack.decode().split(":")[1])
                print(f"Sender: Received ACK: {ack_num}")
                acknowledged.add(ack_num)
                window_base = ack_num + 1

                # Congestion control - AIMD
                if cwnd < ssthresh:
                    cwnd *= 2  # Exponential growth during slow start
                else:
                    cwnd += 1  # Linear growth during congestion avoidance

        except socket.timeout:
            print("Sender: Timeout occurred, retransmitting...")
            ssthresh = max(cwnd // 2, 1)
            cwnd = 1  # Reset to slow start
            # for i in range(window_base, min(window_base + cwnd, len(packets))):
            #     if i not in acknowledged:
            #         packet = f"{i}:{packets[i].decode(errors='ignore')}".encode()
            #         sender_socket.sendto(packet, ("localhost", 12345))
            #         print(f"Sender: Retransmitted packet: {i}")

# Reliable Data Transfer - Receiver

def rdt_receive():
    expected_sequence_number = 0
    receiver_buffer = []  # Simulate a buffer to hold incoming data packets
    while True:
        packet, address = receiver_socket.recvfrom(BUFFER_SIZE)
        if ":" in packet.decode():
            sequence_number, data = packet.decode().split(":", 1)
            sequence_number = int(sequence_number)

            if sequence_number == expected_sequence_number:
                # Add data to buffer if the receiver window allows
                if len(receiver_buffer) < receiver_window:
                    print(f"Receiver: Received packet: {sequence_number}")
                    receiver_buffer.append(data)
                    receiver_socket.sendto(f"ACK:{sequence_number}".encode(), address)
                    expected_sequence_number += 1
                else:
                    # If the window is full, we cannot accept more packets yet
                    print(f"Receiver: Window full, waiting to process packet {sequence_number}...")
                    continue
            else:
                # Send ACK for the last correctly received packet
                ack_to_send = expected_sequence_number - 1
                receiver_socket.sendto(f"ACK:{ack_to_send}".encode(), address)

        elif packet == b"FIN":
            print("Reveiver: connection teardown initiated by sender.")
            receiver_socket.sendto(b"FIN-ACK", address)
            print("Reveiver: connection closed.")
            break
        
def start_reveive():
    print("Reveiver: Waiting for connection...")
    data, sender_address = receiver_socket.recvfrom(BUFFER_SIZE)
    if data == b"SYN":
        print("Reveiver: Received SYN, sending SYN-ACK...")
        receiver_socket.sendto(b"SYN-ACK", sender_address)
        data, _ = receiver_socket.recvfrom(BUFFER_SIZE)
        if data == b"ACK":
            print("Reveiver: Connection established.")
    rdt_receive()
    
    
def start_send():
    print("Sender: Setting up connection. Sending SYN")
    sender_socket.sendto(b"SYN", RECEIVER_ADDRESS)
    data, _ = sender_socket.recvfrom(BUFFER_SIZE)
    if data == b"SYN-ACK":
        sender_socket.sendto(b"ACK", RECEIVER_ADDRESS)
        print("Sender: Connection established. Send ACK")

    # Send Data
    rdt_send(b"Hello, this is a test message for the reliable transfer protocol.")

    # Connection Teardown
    print("Sender: Tearing down connection...")
    sender_socket.sendto(b"FIN", RECEIVER_ADDRESS)
    data, _ = sender_socket.recvfrom(BUFFER_SIZE)
    if data == b"FIN-ACK":
        sender_socket.sendto(b"ACK", RECEIVER_ADDRESS)
        print("Sender: Connection closed.")

# Start Receiver Thread
receiver_thread = threading.Thread(target=start_reveive)
receiver_thread.daemon = True
receiver_thread.start()

# Example Usage
if __name__ == "__main__":
    start_send()