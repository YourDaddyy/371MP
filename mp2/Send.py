import socket
import threading
import random
import time

# Constants
BUFFER_SIZE = 1024
TIMEOUT_INTERVAL = 2  # Timeout interval in seconds
LOSS_PROBABILITY = 0.5  # Probability of packet loss
RECEIVER_ADDRESS = ("localhost", 12345)


# Sequence Number Tracking
next_sequence_number = 0
acknowledged = set()

# Congestion Control Parameters
cwnd = 1
ssthresh = 16



def rdt_send(data, sender_socket):
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

def start_send():
    sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("Sender: Setting up connection. Sending SYN")
    sender_socket.sendto(b"SYN", RECEIVER_ADDRESS)
    data, _ = sender_socket.recvfrom(BUFFER_SIZE)
    if data == b"SYN-ACK":
        sender_socket.sendto(b"ACK", RECEIVER_ADDRESS)
        print("Sender: Connection established. Send ACK")


    rdt_send(b"Hello, this is a test message for the reliable transfer protocol.", sender_socket)

    print("Sender: Tearing down connection...")
    sender_socket.sendto(b"FIN", RECEIVER_ADDRESS)
    data, _ = sender_socket.recvfrom(BUFFER_SIZE)
    if data == b"FIN-ACK":
        sender_socket.sendto(b"ACK", RECEIVER_ADDRESS)
        print("Sender: Connection closed.")

if __name__ == "__main__":
    start_send()
