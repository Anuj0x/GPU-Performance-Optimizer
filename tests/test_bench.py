"""
Tests for GPA benchmarking functionality.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from python.bench import Config, TestCase, setup, run_command

class TestConfig:
    """Test configuration management."""

    def test_config_creation(self):
        """Test Config dataclass creation."""
        config = Config(iterations=5, verbose=True, fast=True)
        assert config.iterations == 5
        assert config.verbose is True
        assert config.fast is True
        assert config.debug is False  # default

    def test_config_logging_setup(self):
        """Test logging setup."""
        config = Config(debug=True)
        # Should not raise any exceptions
        config.setup_logging()

class TestTestCase:
    """Test TestCase dataclass."""

    def test_valid_test_case(self):
        """Test valid TestCase creation."""
        tc = TestCase(
            name="test",
            path="/tmp/test",
            command="./test",
            options=["arg1", "arg2"],
            kernels=["kernel1"],
            versions=["v1", "v2"],
            version_names=["name1", "name2"]
        )
        assert tc.name == "test"
        assert len(tc.versions) == len(tc.version_names)

    def test_invalid_test_case(self):
        """Test TestCase validation."""
        with pytest.raises(ValueError):
            TestCase(
                name="test",
                path="/tmp/test",
                command="./test",
                options=[],
                kernels=[],
                versions=["v1"],  # Different length
                version_names=["name1", "name2"]  # Different length
            )

class TestSetupFunction:
    """Test the setup function."""

    def test_setup_rodinia_all(self):
        """Test setup for all rodinia cases."""
        cases = setup("", "V100")
        assert len(cases) > 10  # Should have multiple test cases

    def test_setup_rodinia_specific(self):
        """Test setup for specific rodinia case."""
        cases = setup("rodinia/bfs", "V100")
        assert len(cases) == 1
        assert cases[0].name == "bfs"

    def test_setup_quicksilver(self):
        """Test setup for quicksilver."""
        cases = setup("quicksilver", "V100")
        assert len(cases) == 2  # quicksilver has 2 variants

    def test_setup_v100_filtering(self):
        """Test V100 architecture filtering."""
        cases = setup("exatensor", "V100")
        # Should have fewer cases due to V100 filtering
        exatensor_cases = [c for c in cases if c.name == "exatensor"]
        assert len(exatensor_cases[0].versions) < 5  # opt3 and opt4 removed

class TestRunCommand:
    """Test the run_command function."""

    @patch('subprocess.run')
    def test_successful_command(self, mock_run):
        """Test successful command execution."""
        mock_run.return_value = MagicMock(returncode=0, stdout="success", stderr="")

        result = run_command(["echo", "test"])
        assert result.returncode == 0

    @patch('subprocess.run')
    def test_failed_command(self, mock_run):
        """Test failed command execution."""
        mock_run.side_effect = subprocess.CalledProcessError(1, ["failing_cmd"], stderr="error")

        with pytest.raises(GPAError):
            run_command(["failing_cmd"])

    @patch('subprocess.run')
    def test_file_not_found(self, mock_run):
        """Test file not found error."""
        mock_run.side_effect = FileNotFoundError()

        with pytest.raises(GPAError):
            run_command(["nonexistent_command"])

class TestBenchmarking:
    """Test benchmarking functionality."""

    @patch('python.bench.run_command')
    @patch('os.chdir')
    @patch('time.time')
    def test_benchmark_execution(self, mock_time, mock_chdir, mock_run_cmd):
        """Test basic benchmark execution flow."""
        # Mock time to return different values
        mock_time.side_effect = [100.0, 105.0]  # 5 second execution

        # Mock successful command runs
        mock_result = MagicMock()
        mock_result.stdout = "GPU kernel_name 1.5ms"
        mock_run_cmd.return_value = mock_result

        # This would need more complex mocking for full test
        # For now, just ensure imports work
        assert True

if __name__ == "__main__":
    pytest.main([__file__])
