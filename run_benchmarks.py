#!/usr/bin/env python3
"""
Modern GPA Benchmark Runner

Handles data setup and benchmark execution with modern Python practices.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List

class BenchmarkRunner:
    """Handles GPA benchmark execution with modern practices."""

    def __init__(self):
        self.project_root = Path.cwd()
        self.benchmark_dir = self.project_root / "GPA-Benchmark"
        self.python_dir = self.project_root / "python"
        self.logger = self._setup_logging()

    def _setup_logging(self):
        """Set up logging for benchmark execution."""
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)

    def run_command(self, command: List[str], cwd: Optional[Path] = None,
                   check: bool = True) -> subprocess.CompletedProcess:
        """Run a command with proper error handling."""
        try:
            self.logger.debug(f"Running: {' '.join(command)}")
            return subprocess.run(
                command,
                cwd=cwd or self.project_root,
                check=check,
                capture_output=False,
                text=True
            )
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {' '.join(command)}")
            self.logger.error(f"Error output: {e.stderr}")
            raise

    def setup_data(self) -> None:
        """Download and set up benchmark data if not present."""
        data_dir = self.benchmark_dir / "data"

        if data_dir.exists():
            self.logger.info("Benchmark data already exists, skipping download")
            return

        self.logger.info("Setting up benchmark data...")

        # Change to benchmark directory
        get_data_script = self.benchmark_dir / "get_data.sh"
        if get_data_script.exists():
            self.logger.info("Running data download script...")
            self.run_command(["bash", str(get_data_script)], cwd=self.benchmark_dir)
        else:
            self.logger.warning("get_data.sh script not found, assuming data is pre-installed")

    def run_benchmarks(self, args: List[str]) -> None:
        """Run the GPA benchmarks with provided arguments."""
        self.logger.info("Running GPA benchmarks...")

        bench_script = self.python_dir / "bench.py"
        if not bench_script.exists():
            raise FileNotFoundError(f"Benchmark script not found: {bench_script}")

        # Run the benchmark script with all passed arguments
        command = [sys.executable, str(bench_script)] + args
        self.run_command(command)

    def run(self, args: List[str]) -> None:
        """Main execution flow."""
        self.logger.info("Starting GPA benchmark execution")

        # Setup data first
        self.setup_data()

        # Run benchmarks
        self.run_benchmarks(args)

        self.logger.info("Benchmark execution completed")

def main():
    """Main entry point for benchmark runner."""
    parser = argparse.ArgumentParser(
        description="Run GPU Performance Advisor Benchmarks",
        add_help=False  # We'll pass through to bench.py
    )

    # Add our specific options
    parser.add_argument(
        '--skip-data-setup',
        action='store_true',
        help='Skip benchmark data setup (assume already downloaded)'
    )

    # Parse known args, pass the rest to bench.py
    known_args, remaining_args = parser.parse_known_args()

    runner = BenchmarkRunner()

    if not known_args.skip_data_setup:
        runner.setup_data()

    runner.run_benchmarks(remaining_args)

if __name__ == "__main__":
    main()
