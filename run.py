import sys
import subprocess
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

from code.server import server

server.launch()