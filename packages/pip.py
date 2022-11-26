import subprocess
import sys


def install(pkg, path):
    return subprocess.check_call(
        [sys.executable, "-m", "pip", "install", pkg, f"--target={path}"]
    )


pkgs = [
    "fyers-apiv2==2.0.5",
]

base = "packages/"
for i in pkgs:
    [name, ver] = i.split("==")
    path = base + name + "/" + ver
    print(path)
    install(i, path)
