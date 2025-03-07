import subprocess
import time

#services = ["router","server1", "client2"]
#services = ["server1", "server2", "server3","server4", "server5"]
#services = ["router","server1", "server2", "server3","server4", "server5","client2"]
services = ["router","server1", "server2", "server3","client2"]
#services = ["server1", "server2", "server3", "server4", "server5", "server6", "server7", "server8", "server9", "server10", "client1"]
#services = ["server1", "server2", "server3", "server4", "server5", "server6", "server7", "server8", "server9", "server10", "server11", "server12", "server13", "server14", "server15", "server16", "server17", "server18", "server19", "server20"]

for service in services:
    print(f"Starting {service}...")
    subprocess.run(["docker-compose", "up", "-d", service])
    subprocess.Popen(["start", "cmd", "/k", "docker logs -f " + service ], shell=True)
    time.sleep(5)  # Espera 5 segundos antes de iniciar el siguiente
print("All services are up!")


#+ " >> " + service + ".txt" cmd", "/k", "docker logs -f router

