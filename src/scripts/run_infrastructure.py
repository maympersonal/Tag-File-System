import subprocess
import time


#services = ["server1", "client1"]
services = ["server1","server2", "server3","client1"]
#services = ["server1", "server2", "server3", "server4", "server5", "server6", "server7", "server8", "server9", "server10", "client1"]


for service in services:
    print(f"Starting {service}...")
    subprocess.run(["docker-compose", "up", "-d", service])
    subprocess.Popen(["start", "cmd", "/k", "docker logs -f " + service], shell=True)
    time.sleep(20)  # Espera 5 segundos antes de iniciar el siguiente
print("All services are up!")
