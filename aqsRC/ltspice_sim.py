import subprocess
import re
from pathlib import Path
import os
import numpy as np

os.chdir('/home/marek/workspace')

netfile='4sim_.net'
NETLIST = Path(netfile)
LOGFILE = Path("4sim.log")
# DOCKER_CMD = [
#     "docker", "run", "--rm",
#     "-v", f"{Path.cwd()}:/work",
#     "-w", "/work",
#     "ltspice",
#     "wine", "ltspice.exe", "-b", "rc.net"
# ]

# DOCKER_CMD = [
#     "docker", "run", "--rm",  #"--user", "$(id -u):$(id -g)",
#     "-v", f"{Path.cwd()}:/workspace",
#     "-w", "/workspace",
#     "docker-ltspice",
#     "wine", "/root/.wine/drive_c/Program Files/ADI/LTspice/Ltspice.exe", "-b", f'./{netfile}'
# ]

DOCKER_CMD = [
    "docker", "run", "--rm", 
    "-v", f"{Path.cwd()}:/workspace",
    "-w", "/workspace",
    "aanas0sayed/docker-ltspice:latest",
    "--entrypoint","wine", r"/root/.wine/drive_c/Program Files/ADI/LTspice/Ltspice.exe", #"-b", f'./{netfile}'
]
# docker run -it \
#   --name ltspice \
#   --hostname "$HOSTNAME" \
#   -e DISPLAY=:0 \
#   -e QT_X11_NO_MITSHM=1 \
#   -v /home/marek/workspace:/workspace \
#   -v /tmp/.X11-unix:/tmp/.X11-unix \
#   -w /workspace \
#   --shm-size=512m \
#   aanas0sayed/docker-ltspice:latest

# ltspice is aliased to `wine "/root/.wine/drive_c/Program Files/ADI/LTspice/Ltspice.exe"'

def run_sim(R):
    text = NETLIST.read_text(encoding="cp1252")
    text = re.sub(r"\.param Rs=.*", f".param Rs={R}", text)
    NETLIST.write_text(text)

    subprocess.run(DOCKER_CMD, check=True)

    log = LOGFILE.read_text()
    avg = re.search(r"Vout_avg:\s*([0-9eE+.-]+)", log)

    return float(avg.group(1))


R_values=[r for r in np.arange(1.0,10.0,1.)]

for R in R_values:
    avg, pp = run_sim(R)
    print(f"{R:10.1f} | {avg:12.6f} | {pp:10.6f}")






