from socket import *
import os
import struct
import time
import matplotlib.pyplot as plt


path = r'E:\second year\2 nd semester\Network\network project\small file.jpeg'
recvrIP = 'localhost'  # Receiver IP address
recvrPort = 1234  # Receiver port
mss = 1024  # Maximum Segment Size
windowSize = 4  # Window size
timeOut = 2  # Timeout interval
fileID = 123  # File ID

# Open the file and read data
with open(path, 'rb') as file:
    img_data = file.read()

# Create a socket
sender = socket(AF_INET, SOCK_DGRAM)
sender.settimeout(timeOut)

# Calculate total packets needed
total_packets = (len(img_data) + mss - 1) // mss
base = 0
next_seq_num = 0

# Lists  packet IDs and time  
packet_times = []
packet_ids = []

# create packets
def create_packet(seq_num, data, last_packet=False):
    packet_id = struct.pack('!H', seq_num)
    file_id = struct.pack('!H', fileID)
    trailer = struct.pack('!I', 0xFFFF if last_packet else 0x0000)
    return packet_id + file_id + data + trailer


try:
    while base < total_packets:

        while next_seq_num < base + windowSize and next_seq_num < total_packets:

            start = next_seq_num * mss
            end = min((next_seq_num + 1) * mss, len(img_data))
            packet_data = create_packet(next_seq_num, img_data[start:end], last_packet=(next_seq_num == total_packets - 1))
            sender.sendto(packet_data, (recvrIP, recvrPort))


            # Log the send time and packet ID
            packet_times.append(time.time())
            packet_ids.append(next_seq_num)
            next_seq_num += 1

        try:
            while True:

                ack_packet, _ = sender.recvfrom(2048)
                ack_id = struct.unpack('!H', ack_packet[:2])[0]
                if ack_id >= base:
                    base = ack_id + 1
                    break


        except timeout:
            for i in range(base, next_seq_num):
                start = i * mss
                end = min((i + 1) * mss, len(img_data))
                packet_data = create_packet(i, img_data[start:end], last_packet=(i == total_packets - 1))
                sender.sendto(packet_data, (recvrIP, recvrPort))
                
                
finally:
    sender.close()

# to intialize the start time
start_time = packet_times[0]
packet_times = [t - start_time for t in packet_times]

# visualize
plt.figure(figsize=(10, 5))
plt.plot(packet_times, packet_ids, marker='o')
plt.xlabel('Time (seconds)')
plt.ylabel('Packet ID')
plt.title('Packet Transmission Time vs. Packet ID')
plt.grid(True)
plt.show()

print("File transmission completed.")
