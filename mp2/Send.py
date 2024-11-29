import socket
import threading
import random
import time

# Constants
BUFFER_SIZE = 1024
TIMEOUT_INTERVAL = 2  # Timeout interval in seconds
LOSS_PROBABILITY = 0.2  # Probability of packet loss
RECEIVER_ADDRESS = ("localhost", 12345)


# Sequence Number Tracking
next_sequence_number = 0
acknowledged = set()

# Congestion Control Parameters
cwnd = 1
ssthresh = 16

def send_packet(i, packet_data, sender_socket):
    global next_sequence_number
    if i not in acknowledged:
        # Simulate packet loss
        if random.random() > LOSS_PROBABILITY:
            packet = f"{i}:{packet_data.decode(errors='ignore')}".encode()
            sender_socket.sendto(packet, RECEIVER_ADDRESS)
            print(f"Sender: Sent packet: {i}")
        else:
            print(f"Sender: Packet {i} lost")


def rdt_send(data, sender_socket):
    global next_sequence_number, cwnd, ssthresh

    # Split data into packets
    packets = [data[i:i + 128] for i in range(0, len(data), 128)]
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
        
        # threads = []
        
        # # Send packets in parallel within the window
        # for i in range(window_base, min(window_base + cwnd, len(packets))):
        #     if i not in acknowledged:
        #         # Create a new thread to send the packet
        #         thread = threading.Thread(target=send_packet, args=(i, packets[i], sender_socket))
        #         threads.append(thread)
        #         thread.start()

        # # Wait for all threads to complete
        # for thread in threads:
        #     thread.join()
        num_sent_packets = 0
        for i in range(window_base, min(window_base + cwnd, len(packets))):
            if i not in acknowledged:
                num_sent_packets += 1
                # Simulate packet loss
                if random.random() > LOSS_PROBABILITY:
                    packet = f"{i}:{packets[i].decode(errors='ignore')}".encode()
                    sender_socket.sendto(packet, ("localhost", 12345))
                    print(f"Sender: Sent packet: {i}")
                else:
                    print(f"Sender: Packet {i} lost")

        # Wait for ACKs
        # try:
        #     sender_socket.settimeout(TIMEOUT_INTERVAL)
        #     ack, _ = sender_socket.recvfrom(BUFFER_SIZE)
        #     if ":" in ack.decode():
        #         ack_num = int(ack.decode().split(":")[1])
        #         print()
        #         print(f"Sender: Received ACK: {ack_num}")
        #         print()
        #         acknowledged.add(ack_num)
        #         window_base = ack_num + 1

        #         # Congestion control - AIMD
        #         if cwnd < ssthresh:
        #             cwnd *= 2  # Exponential growth during slow start
        #         else:
        #             cwnd += 1  # Linear growth during congestion avoidance

        # except socket.timeout:
        #     print()
        #     print("Sender: Timeout occurred, retransmitting...")
        #     print()
        #     ssthresh = max(cwnd // 2, 1)
        #     cwnd = 1  # Reset to slow start
        #     # for i in range(window_base, min(window_base + cwnd, len(packets))):
        #     #     if i not in acknowledged:
        #     #         packet = f"{i}:{packets[i].decode(errors='ignore')}".encode()
        #     #         sender_socket.sendto(packet, ("localhost", 12345))
        #     #         print(f"Sender: Retransmitted packet: {i}")
        
        # Update congestion control parameters
        if cwnd < ssthresh:
            cwnd *= 2  # Exponential growth during slow start
        else:
            cwnd += 1  # Linear growth during congestion avoidance
            
        start_time = time.time()
        received_acks = set()
        print()
        while time.time() - start_time < 3 and len(received_acks) < num_sent_packets:
            try:
                sender_socket.settimeout(TIMEOUT_INTERVAL)
                ack = None
                ack, _ = sender_socket.recvfrom(BUFFER_SIZE)
                if ":" in ack.decode():
                    ack_num = int(ack.decode().split(":")[1])
                    print(f"Sender: Received ACK: {ack_num}")
                    received_acks.add(ack_num)
            except socket.timeout:
                print("Sender: Timeout occurred, retransmitting...")
                ssthresh = max(cwnd // 2, 1)
                cwnd = 1
                break
        print()
        # Process all received ACKs
        received_acks = sorted(received_acks)
        for ack_num in received_acks:
            acknowledged.add(ack_num)
            window_base = ack_num + 1
            

        # Check if there are still unacknowledged packets
        if window_base >= len(packets):
            print("All packets acknowledged.")
            break  # Exit the loop when all packets are acknowledged

def start_send():
    sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("Sender: Setting up connection. Sending SYN")
    sender_socket.sendto(b"SYN", RECEIVER_ADDRESS)
    data, _ = sender_socket.recvfrom(BUFFER_SIZE)
    if data == b"SYN-ACK":
        sender_socket.sendto(b"ACK", RECEIVER_ADDRESS)
        print("Sender: Connection established. Send ACK")


    rdt_send(b"Using Convolutional Neural Networks for sonar data detection provides a robust solution for real-time analysis. As suggested in, such models as YOLO, Faster R- CNN , and SSD designed for rapid object detection, align well with the demands of sonar applications, where swift and accurate identification of objects is critical. This models inherent capability to handle various data types ensures efficient processing of sonar signals and reliable detection results once adapted. We adopt YOLOv8 as our base model for on-premise in- ference, with our converted 3 channels as input. As shown in Figure 8, YOLOv8 includes features from previous ver- sions, such as Multi-Scale Predictions (v3), PANet (v4), and the Efficient Layer Aggregation Network (ELAN) (v7), while improving ease and uniformity of on-site commissioning. Its modularity simplifies system construction. YOLOv8s archi- tecture is similar to earlier versions, with the addition of the c2f block for better feature extraction and aggregation. As an anchor-free model, YOLOv8 reduces candidate bounding boxes, effectively lowering false positives in high-noise sonar environments. Additionally, the lightweight architecture of YOLOv8 en- sures low latency and rapid inference, making it ideal for deployment on edge devices like the Jetson Orin Nano [ 23]. These devices are optimized for edge AI applications, offering the necessary computational power while maintaining low energy consumption and thermal efficiency. All these make YOLOv8 a robust solution for real-time sonar data analysis, providing immediate and accurate insights that are critical for various applications.FFN Current Frame Ref Frame 1 Ref Frame 2 x N x N x N Query Decoder Current Frame Current Frame Key Sampling Points Encoder Inference Flow Query Self-attention Multi-head Attention Memory Memory Self-attention", sender_socket)

    print("Sender: Tearing down connection...")
    sender_socket.sendto(b"FIN", RECEIVER_ADDRESS)
    data, _ = sender_socket.recvfrom(BUFFER_SIZE)
    if data == b"FIN-ACK":
        sender_socket.sendto(b"ACK", RECEIVER_ADDRESS)
        print("Sender: Connection closed.")

if __name__ == "__main__":
    start_send()
