"""
launcher.py — 单容器同时跑 server.py（MCP，8000）和 gateway.py（Gateway，8010）。

一个 Docker CMD 只能起一个前台进程，但这个 fork 需要两个服务同时在线。
这里用两个子进程各自把 stdout/stderr 转发给容器日志，任何一个异常退出就整体退出
（避免"网关挂了但container还显示健康"的假活状态），收到 SIGTERM/SIGINT 时优雅关两个。
"""

import signal
import subprocess
import sys
import time

_procs: list[subprocess.Popen] = []


def _log(msg: str) -> None:
    print(f"[LAUNCHER] {msg}", flush=True)


def _start(name: str, script: str) -> subprocess.Popen:
    _log(f"starting {script}")
    proc = subprocess.Popen(
        [sys.executable, script],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    _log(f"{name} pid={proc.pid}")
    return proc


def _shutdown(*_args) -> None:
    _log("shutting down")
    for proc in _procs:
        if proc.poll() is None:
            proc.terminate()
    for proc in _procs:
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
    sys.exit(0)


def main() -> None:
    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    gateway = _start("gateway", "gateway.py")
    _procs.append(gateway)
    time.sleep(2)
    if gateway.poll() is not None:
        _log(f"gateway exited early with code {gateway.returncode}")
        sys.exit(gateway.returncode or 1)
    _log("gateway running ok")

    server = _start("server", "server.py")
    _procs.append(server)

    # 任何一个先退出，都整体退出（进程互相是对方的健康标志）
    while True:
        for proc, name in ((gateway, "gateway"), (server, "server")):
            code = proc.poll()
            if code is not None:
                _log(f"{name} exited with code {code}, shutting down the other one")
                other = server if proc is gateway else gateway
                if other.poll() is None:
                    other.terminate()
                    try:
                        other.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        other.kill()
                sys.exit(code or 1)
        time.sleep(1)


if __name__ == "__main__":
    main()
