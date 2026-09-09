#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.gate_interceptor import run_gated, GateVetoException


class TestGateInterceptor(unittest.TestCase):

    def test_nominal_execution(self):
        """Standard valid command returns CompletedProcess without veto."""
        res = run_gated(["echo", "gate_ok"], action="TEST_NOMINAL")
        self.assertEqual(res.returncode, 0)
        self.assertIn("gate_ok", res.stdout)

    def test_posix_126_veto_trapped(self):
        """Exit code 126 must raise GateVetoException (POSIX statutory veto)."""
        mock_proc = MagicMock()
        mock_proc.returncode = 126
        mock_proc.stdout = ""
        mock_proc.stderr = "Execution vetoed by statutory charter policy."

        with patch("subprocess.run", return_value=mock_proc):
            with self.assertRaises(GateVetoException) as ctx:
                run_gated(["unauthorized_action"], action="TEST_VETO")
            self.assertIn("Statutory Veto (Exit 126)", str(ctx.exception))
            self.assertIn("TEST_VETO", str(ctx.exception))

    def test_subshell_exit_126_live(self):
        """Direct subshell returning 126 triggers GateVetoException on live subprocess."""
        # Using sh -c 'exit 126' to produce a clean POSIX 126 exit code
        with self.assertRaises(GateVetoException):
            run_gated(["sh", "-c", "exit 126"], action="FORCED_VETO")

    def test_standard_non_zero_not_veto(self):
        """Exit code 1 should return normal process output, not raise GateVetoException."""
        res = run_gated(["sh", "-c", "exit 1"], action="TEST_FAIL")
        self.assertEqual(res.returncode, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
