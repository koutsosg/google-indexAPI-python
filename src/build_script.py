import subprocess

def build():
    subprocess.run(["pyinstaller", "--onefile", "src/indexing.py"], check=True)