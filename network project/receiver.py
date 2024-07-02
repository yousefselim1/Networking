import socket
import struct
import random
import os
import time
import matplotlib.pyplot as plt


recvrIP = 'localhost'  # Receiver IP address
recvrPort = 1234  # Receiver port
loss_rate = random.uniform(0.05, 0.15)  # packet loss rate
buffer_size = 2048  # Buffer size 

# Create the socket 
receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver.bind((recvrIP, recvrPort))

expected_seq_num = 0
received_file = bytearray()
packet_times = []  # List packet time
packet_ids = []  # List

print("Waiting to receive file...")

try:
    while True:
        # Receive packet
        packet, addr = receiver.recvfrom(buffer_size)
        
        #  packet loss
        if random.random() < loss_rate:
            print(f"Packet with sequence number {expected_seq_num} dropped")
            continue
        
    
        packet_id = struct.unpack('!H', packet[:2])[0]
        file_id = struct.unpack('!H', packet[2:4])[0]
        trailer = struct.unpack('!I', packet[-4:])[0]
        data = packet[4:-4]
        receive_time = time.time()

        # Check for the packet
        if packet_id == expected_seq_num:
            print(f"Received packet {packet_id} correctly")
            received_file.extend(data)
            expected_seq_num += 1

            
            packet_times.append(receive_time)
            packet_ids.append(packet_id)

            # Send acknowledgment for the received packet
            ack_packet = struct.pack('!H', expected_seq_num - 1)
            receiver.sendto(ack_packet, addr)

            # Check for the end
            if trailer == 0xFFFF:
                # Write to file
                with open('received_file.jpeg', 'wb') as f:
                    f.write(received_file)
                print("File reception complete. File saved as 'received_file.jpeg'.")
                
                if 'received_file.jpeg'.endswith(('.jpeg')):
                    os.startfile('received_file.jpeg')  # the image
                break
        else:
            print(f"Received out-of-order packet {packet_id}. Expected {expected_seq_num}")
            # Send acknowledgment for the last received packet
            ack_packet = struct.pack('!H', expected_seq_num - 1)
            receiver.sendto(ack_packet, addr)

finally:
    receiver.close()
    print("Receiver closed.")

# to intialize the start time
    start_time = packet_times[0]
    packet_times = [t - start_time for t in packet_times]

    # visualize
    plt.figure(figsize=(10, 5))
    plt.plot(packet_times, packet_ids, marker='o')
    plt.xlabel('Time (seconds since start)')
    plt.ylabel('Packet ID')
    plt.title('Time vs. Packet ID at Receiver')
    plt.grid(True)
    plt.show()
