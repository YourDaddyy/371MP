import socket
import random
import time

# Constants
BUFFER_SIZE = 1024
TIMEOUT_INTERVAL = 2  # Timeout interval in seconds
LOSS_PROBABILITY = 0.1  # Probability of packet loss
RECEIVER_ADDRESS = ("localhost", 12345)  # Receiver address

# Congestion Control Parameters
cwnd = 1
ssthresh = 16

# Reliable Data Transfer - Sender
def rdt_send(sender_socket, data):
    global cwnd, ssthresh
    packets = [data[i:i + BUFFER_SIZE] for i in range(0, len(data), BUFFER_SIZE)]
    window_base = 0
    acknowledged = set()

    while window_base < len(packets):
        # Send packets in the current congestion window
        for i in range(window_base, min(window_base + cwnd, len(packets))):
            if i not in acknowledged:
                if random.random() > LOSS_PROBABILITY:
                    packet = f"{i}:{packets[i].decode(errors='ignore')}".encode()
                    sender_socket.sendto(packet, RECEIVER_ADDRESS)
                    print(f"Sent packet: {i}")
                else:
                    print(f"Packet {i} lost")

        # Wait for ACKs
        try:
            sender_socket.settimeout(TIMEOUT_INTERVAL)
            ack, _ = sender_socket.recvfrom(BUFFER_SIZE)
            if ":" in ack.decode():
                ack_num = int(ack.decode().split(":")[1])
                print(f"Received ACK: {ack_num}")
                acknowledged.add(ack_num)
                if ack_num >= window_base:
                    window_base = ack_num + 1

                # Congestion control: AIMD
                if cwnd < ssthresh:
                    cwnd *= 2  # Exponential growth
                else:
                    cwnd += 1  # Linear growth

        except socket.timeout:
            print("Timeout occurred, retransmitting...")
            ssthresh = max(cwnd // 2, 1)
            cwnd = 1  # Slow start
            # Retransmit unacknowledged packets
            for i in range(window_base, min(window_base + cwnd, len(packets))):
                if i not in acknowledged:
                    packet = f"{i}:{packets[i].decode(errors='ignore')}".encode()
                    sender_socket.sendto(packet, RECEIVER_ADDRESS)
                    print(f"Retransmitted packet: {i}")

# Main Function
if __name__ == "__main__":
    sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Connection Setup
    print("Setting up connection...")
    sender_socket.sendto(b"SYN", RECEIVER_ADDRESS)
    data, _ = sender_socket.recvfrom(BUFFER_SIZE)
    if data == b"SYN-ACK":
        sender_socket.sendto(b"ACK", RECEIVER_ADDRESS)
        print("Connection established.")

    # Send Data
    rdt_send(sender_socket, b"Hello, this is a test message for the reliable transfer protocol.")

    # Connection Teardown
    print("Tearing down connection...")
    sender_socket.sendto(b"FIN", RECEIVER_ADDRESS)
    data, _ = sender_socket.recvfrom(BUFFER_SIZE)
    if data == b"FIN-ACK":
        sender_socket.sendto(b"ACK", RECEIVER_ADDRESS)
        print("Connection closed.")
