#!/bin/bash

# ICMP Flood DoS Test Script (Localhost)

DURATION=15        # seconds to run the test
TARGET_IP="127.0.0.1"
PCAP_FILE="icmp_flood.pcap"

echo "[*] Starting ICMP flood test on $TARGET_IP"
echo "[*] Logging packets to $PCAP_FILE"

# Start tcpdump in background
sudo tcpdump -i lo icmp -w $PCAP_FILE &
TCPDUMP_PID=$!

# Launch htop and iftop in separate terminals (if installed)
if command -v x-terminal-emulator &>/dev/null; then
    x-terminal-emulator -e htop &
    x-terminal-emulator -e "sudo iftop -i lo" &
elif command -v gnome-terminal &>/dev/null; then
    gnome-terminal -- htop &
    gnome-terminal -- sudo iftop -i lo &
else
    echo "[!] No supported terminal emulator found for launching htop/iftop."
fi

# Wait a moment to let tcpdump start
sleep 2

# Start ICMP flood
sudo hping3 -1 --flood -d 2000 $TARGET_IP &
HPING_PID=$!

# Let it run
sleep $DURATION

# Stop hping3 and tcpdump
echo "[*] Stopping test..."
sudo kill $HPING_PID
sudo kill $TCPDUMP_PID

echo "[✓] Test completed."
echo "[✓] Packet capture saved to $PCAP_FILE"
