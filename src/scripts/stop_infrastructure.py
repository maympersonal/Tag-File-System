import subprocess

print("Stopping and removing all containers...")
subprocess.run(["docker-compose", "down"])
print("All containers stopped and removed.")
