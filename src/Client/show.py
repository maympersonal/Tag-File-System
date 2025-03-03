import subprocess
import time

subprocess.Popen("start cmd /k docker logs -f server_miguel1", shell=True)
subprocess.Popen("start cmd /k docker logs -f server_miguel2", shell=True)
subprocess.Popen("start cmd /k docker logs -f server_miguel3", shell=True)
