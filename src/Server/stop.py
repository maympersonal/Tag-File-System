import subprocess
import time

subprocess.run("docker stop server_miguel1", shell=True)
subprocess.run("docker stop server_miguel2", shell=True)
subprocess.run("docker stop server_miguel3", shell=True)
