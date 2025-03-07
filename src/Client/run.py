import subprocess
import time

subprocess.run("docker run --rm --name client_miguel1 --cap-add NET_ADMIN --network clients -it client_miguel", shell=True)
