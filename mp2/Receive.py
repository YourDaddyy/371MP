import socket

# Constants
BUFFER_SIZE = 1024
RECEIVER_ADDRESS = ("localhost", 12345)  # Receiver address
receiver_window = 5  # Flow control: buffer size

# Reliable Data Transfer - Receiver
def rdt_receive(receiver_socket):
    expected_sequence_number = 0
    receiver_buffer = []  # Simulate a buffer

    while True:
        packet, sender_address = receiver_socket.recvfrom(BUFFER_SIZE)
        if ":" in packet.decode():
            sequence_number, data = packet.decode().split(":", 1)
            sequence_number = int(sequence_number)

            if sequence_number == expected_sequence_number:
                print(f"Received packet: {sequence_number}")
                receiver_buffer.append(data)
                receiver_socket.sendto(f"ACK:{sequence_number}".encode(), sender_address)
                expected_sequence_number += 1
            else:
                # Send ACK for the last correctly received packet
                ack_to_send = expected_sequence_number - 1
                receiver_socket.sendto(f"ACK:{ack_to_send}".encode(), sender_address)

        elif packet == b"FIN":
            print("Connection teardown initiated by sender.")
            receiver_socket.sendto(b"FIN-ACK", sender_address)
            print("Connection closed.")
            break

# Main Function
if __name__ == "__main__":
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver_socket.bind(RECEIVER_ADDRESS)

    # Connection Setup
    print("Waiting for connection...")
    data, sender_address = receiver_socket.recvfrom(BUFFER_SIZE)
    if data == b"SYN":
        print("Received SYN, sending SYN-ACK...")
        receiver_socket.sendto(b"SYN-ACK", sender_address)
        data, _ = receiver_socket.recvfrom(BUFFER_SIZE)
        if data == b"ACK":
            print("Connection established.")

    # Receive Data
    rdt_receive(receiver_socket)
