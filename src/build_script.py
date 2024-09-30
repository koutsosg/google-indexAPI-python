import subprocess

def build():
    subprocess.run(["pyinstaller", "--onefile", "--noconsole", "src/indexing.py"], check=True)