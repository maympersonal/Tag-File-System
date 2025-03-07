import subprocess
import time

<<<<<<< Updated upstream

#services = ["server1", "client1"]
services = ["server1","server2", "server3","client1"]
=======
#services = ["router","server1", "client2"]
#services = ["server1", "server2", "server3","server4", "server5"]
#services = ["router","server1", "server2", "server3","server4", "server5","client2"]
services = ["router","server1", "server2", "server3","client2"]
>>>>>>> Stashed changes
#services = ["server1", "server2", "server3", "server4", "server5", "server6", "server7", "server8", "server9", "server10", "client1"]


for service in services:
    print(f"Starting {service}...")
    subprocess.run(["docker-compose", "up", "-d", service])
    subprocess.Popen(["start", "cmd", "/k", "docker logs -f " + service], shell=True)
    time.sleep(20)  # Espera 5 segundos antes de iniciar el siguiente
print("All services are up!")
