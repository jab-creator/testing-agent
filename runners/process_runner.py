from __future__ import annotations
import subprocess
import os
import time
import signal
from dataclasses import dataclass

@dataclass
class ProcessHandle:
    popen: subprocess.Popen


class ProcessRunner:
    @staticmethod
    def start(command: str, cwd: str):
        # Start in its own process group so we can kill the whole group.
        popen = subprocess.Popen(
            command,
            cwd=cwd,
            shell=True,
            start_new_session=True,  # <-- key on Linux/WSL
        )
        return ProcessHandle(popen=popen)

    @staticmethod
    def stop(handle: ProcessHandle, timeout_s: float = 3.0):
        if not handle or not handle.popen:
            return

        p = handle.popen

        # Already exited?
        if p.poll() is not None:
            return

        try:
            # Kill the whole process group first
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)
        except Exception:
            try:
                p.terminate()
            except Exception:
                pass

        # Wait a bit
        end = time.time() + timeout_s
        while time.time() < end:
            if p.poll() is not None:
                return
            time.sleep(0.1)

        # Hard kill if still alive
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
