"""
Admission Gate Interceptor for sovereign-manifold.
Forces subshell actions through deterministic admission-gate verification.
Traps exit code 126 as a statutory ultra-vires breach.
"""

import os
import shutil
import subprocess
from typing import List, Optional


class GateVetoException(Exception):
    """Raised when an execution payload is vetoed by the admission gate (POSIX 126)."""
    pass


def run_gated(
    cmd: List[str],
    resource: Optional[str] = None,
    action: str = "SHELL_EXEC",
    charter_path: Optional[str] = None,
    sock_path: Optional[str] = None,
    timeout: float = 45.0,
    check: bool = False
) -> subprocess.CompletedProcess:
    """
    Executes a command vector wrapped inside admission-gate.
    Passes required --resource and optional --action/--charter/--sock.
    """
    gate_bin = shutil.which("admission-gate")
    
    if gate_bin:
        target_resource = resource or (cmd[0] if cmd else "unknown")
        exec_vector = [gate_bin, "exec", "--action", action, "--resource", target_resource]

        if charter_path and os.path.exists(charter_path):
            exec_vector.extend(["--charter", charter_path])
        elif sock_path and os.path.exists(sock_path):
            exec_vector.extend(["--sock", sock_path])

        exec_vector.append("--")
        exec_vector.extend(cmd)
    else:
        exec_vector = cmd

    res = subprocess.run(
        exec_vector,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout
    )

    if res.returncode == 126:
        raise GateVetoException(
            f"Statutory Veto (Exit 126): Action {action} on {resource or cmd} rejected by admission-gate.\n"
            f"Stderr: {res.stderr.strip()}"
        )

    if check and res.returncode != 0:
        raise subprocess.CalledProcessError(
            res.returncode, exec_vector, output=res.stdout, stderr=res.stderr
        )

    return res
