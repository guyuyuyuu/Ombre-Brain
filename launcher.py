import subprocess, sys, os, signal, time

print("[LAUNCHER] starting gateway.py", flush=True)
gw = subprocess.Popen(
    [sys.executable, "gateway.py"],
    stdout=sys.stdout, stderr=sys.stderr,
)
print(f"[LAUNCHER] gateway pid={gw.pid}", flush=True)
time.sleep(2)
if gw.poll() is not None:
    print(f"[LAUNCHER] gateway exited early with code {gw.returncode}", flush=True)
else:
    print("[LAUNCHER] gateway running ok", flush=True)

print("[LAUNCHER] starting server.py", flush=True)
sv = subprocess.Popen(
    [sys.executable, "server.py"],
    stdout=sys.stdout, stderr=sys.stderr,
)
print(f"[LAUNCHER] server pid={sv.pid}", flush=True)

def _shutdown(sig, frame):
    gw.terminate()
    sv.terminate()

signal.signal(signal.SIGTERM, _shutdown)
sv.wait()
gw.terminate()
