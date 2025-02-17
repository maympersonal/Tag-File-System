import subprocess

services = ["server1", "server2", "server3", "server4", "server5", "client1", "client2"]

print("Monitoring logs... (Press Ctrl+C to exit)")
try:
    for service in services:
        print(f"Logs for {service}:")
        subprocess.run(["docker", "logs", "-f", service])
except KeyboardInterrupt:
    print("Stopped log monitoring.")
