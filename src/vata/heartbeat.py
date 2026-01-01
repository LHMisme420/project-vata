import time
import sys

def start_pulse():
    print("\n[VATA HEARTBEAT INITIATED]")
    try:
        while True:
            # The 'Pulse' effect using ANSI escape codes for color
            sys.stdout.write("\r\033[92m?? SYSTEM STABLE\033[0m")
            time.sleep(0.5)
            sys.stdout.write("\r\033[90m?? SYSTEM STABLE\033[0m")
            time.sleep(0.5)
            sys.stdout.flush()
    except KeyboardInterrupt:
        print("\n[!] Heartbeat paused by User.")
