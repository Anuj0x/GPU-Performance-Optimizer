#!/usr/bin/env python3
"""
Modern GPA Installation Script

Cross-platform installer for GPU Performance Advisor with proper error handling
and modern Python practices.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, List

class GPAInstaller:
    """Handles GPA installation with modern Python practices."""

    def __init__(self, install_dir: Path, spack_dir: Optional[Path] = None):
        self.install_dir = install_dir
        self.spack_dir = spack_dir
        self.source_dir = Path.cwd()
        self.logger = self._setup_logging()

    def _setup_logging(self):
        """Set up logging for installation process."""
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)

    def run_command(self, command: List[str], cwd: Optional[Path] = None,
                   check: bool = True, env: Optional[dict] = None) -> subprocess.CompletedProcess:
        """Run a command with proper error handling."""
        try:
            self.logger.debug(f"Running: {' '.join(command)}")
            result = subprocess.run(
                command,
                cwd=cwd,
                check=check,
                capture_output=True,
                text=True,
                env=env
            )
            return result
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {' '.join(command)}")
            self.logger.error(f"Error output: {e.stderr}")
            raise

    def install_spack_dependencies(self, spack_root: Path) -> Path:
        """Install required Spack dependencies."""
        self.logger.info("Installing Spack dependencies...")

        # Set up environment
        spack_bin = spack_root / "bin" / "spack"
        env = os.environ.copy()
        env['SPACK_ROOT'] = str(spack_root)
        env['PATH'] = f"{spack_root}/bin:{env['PATH']}"

        # Source spack setup
        setup_script = spack_root / "share" / "spack" / "setup-env.sh"
        if setup_script.exists():
            # For bash-compatible systems
            setup_cmd = f"source {setup_script} && env"
            result = self.run_command(["bash", "-c", setup_cmd], env=env)
            # Parse environment variables from output
            for line in result.stdout.splitlines():
                if '=' in line:
                    key, value = line.split('=', 1)
                    env[key] = value

        # Install dependencies
        self.run_command([
            str(spack_bin), "install", "--only", "dependencies",
            "hpctoolkit", "^dyninst@master", "^binutils@2.34+libiberty~nls"
        ], env=env)

        self.run_command([
            str(spack_bin), "install", "libmonitor@master+dlopen+hpctoolkit"
        ], env=env)

        self.run_command([str(spack_bin), "install", "mbedtls", "gotcha"], env=env)

        # Find spack libraries directory
        result = self.run_command([str(spack_bin), "find", "--path", "boost"],
                                env=env, capture_output=True)
        boost_path = result.stdout.strip().split()[-1]
        spack_libs_dir = Path(boost_path).parent

        self.logger.info(f"Spack libraries installed in: {spack_libs_dir}")
        return spack_libs_dir

    def install_hpctoolkit(self, spack_libs_dir: Path) -> None:
        """Install HPCToolkit from source."""
        self.logger.info("Installing HPCToolkit...")

        hpctoolkit_dir = self.source_dir / "hpctoolkit"
        build_dir = hpctoolkit_dir / "build"

        if not hpctoolkit_dir.exists():
            self.logger.error("HPCToolkit source not found. Make sure submodules are initialized.")
            raise FileNotFoundError("HPCToolkit source directory missing")

        # Clean previous build
        if build_dir.exists():
            shutil.rmtree(build_dir)
        build_dir.mkdir()

        # Configure
        cuda_path = Path("/usr/local/cuda")
        cupti_path = cuda_path / "extras" / "CUPTI"

        configure_cmd = [
            "../configure",
            f"--prefix={self.install_dir}/hpctoolkit",
            f"--with-cuda={cuda_path}",
            f"--with-cupti={cupti_path}",
            f"--with-spack={spack_libs_dir}"
        ]

        self.run_command(configure_cmd, cwd=build_dir)

        # Build and install
        self.run_command(["make", "install", "-j8"], cwd=build_dir)

        self.logger.info(f"HPCToolkit installed in: {self.install_dir}/hpctoolkit")

    def setup_spack(self) -> Path:
        """Clone and set up Spack if not provided."""
        spack_dir = self.install_dir / "spack"

        if self.spack_dir:
            self.logger.info(f"Using existing Spack installation: {self.spack_dir}")
            return self.spack_dir

        self.logger.info("Cloning Spack...")
        self.run_command(["git", "clone", "https://github.com/spack/spack.git"],
                        cwd=self.install_dir)

        spack_root = self.install_dir / "spack"
        return spack_root

    def copy_binaries(self) -> None:
        """Copy GPA binaries to installation directory."""
        src_bin = self.source_dir / "bin"
        dst_bin = self.install_dir / "bin"

        if src_bin.exists():
            if dst_bin.exists():
                shutil.rmtree(dst_bin)
            shutil.copytree(src_bin, dst_bin)
            self.logger.info(f"Copied binaries to: {dst_bin}")
        else:
            self.logger.warning("Source bin directory not found")

    def install(self) -> None:
        """Main installation process."""
        self.logger.info(f"Installing GPA to: {self.install_dir}")

        # Create installation directory
        self.install_dir.mkdir(parents=True, exist_ok=True)

        # Setup Spack
        spack_root = self.setup_spack()

        # Install dependencies
        spack_libs_dir = self.install_spack_dependencies(spack_root)

        # Install HPCToolkit
        self.install_hpctoolkit(spack_libs_dir)

        # Copy binaries
        self.copy_binaries()

        self.logger.info("GPA installation completed successfully!")
        self.logger.info(f"Add to PATH: export PATH={self.install_dir}/bin:$PATH")
        self.logger.info(f"Add GPA path: export GPA={self.install_dir}")

def main():
    parser = argparse.ArgumentParser(description="Install GPU Performance Advisor")
    parser.add_argument(
        "install_dir",
        type=Path,
        help="Installation directory"
    )
    parser.add_argument(
        "--spack-dir",
        type=Path,
        help="Existing Spack installation directory (optional)"
    )

    args = parser.parse_args()

    installer = GPAInstaller(args.install_dir, args.spack_dir)
    installer.install()

if __name__ == "__main__":
    main()
