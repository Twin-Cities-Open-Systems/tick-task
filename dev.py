#!/usr/bin/env python3
"""
Development server wrapper for FIN-tasks.

This script starts both the backend (FastAPI) and frontend (React/Vite) servers
for development. It handles dependency checking, process management, and graceful
shutdown.
"""

import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional


class DevServer:
    """Development server manager for FIN-tasks."""

    def __init__(self, backend_only: bool = False, frontend_only: bool = False):
        self.backend_only = backend_only
        self.frontend_only = frontend_only
        self.backend_process: Optional[subprocess.Popen] = None
        self.frontend_process: Optional[subprocess.Popen] = None
        self.project_root = Path(__file__).parent

    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed."""
        print("🔍 Checking dependencies...")

        # Check Python dependencies
        try:
            import fastapi
            import pydantic
            import sqlalchemy

            print("✅ Python dependencies installed")
        except ImportError as e:
            print(f"❌ Missing Python dependency: {e}")
            print("Run: pip install -e .")
            return False

        # Check Node.js and npm
        try:
            result = subprocess.run(
                ["node", "--version"], capture_output=True, text=True, check=True
            )
            print(f"✅ Node.js installed: {result.stdout.strip()}")

            result = subprocess.run(
                ["npm", "--version"], capture_output=True, text=True, check=True
            )
            print(f"✅ npm installed: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Node.js or npm not found")
            print("Please install Node.js from https://nodejs.org/")
            return False

        return True

    def install_frontend_deps(self) -> bool:
        """Install frontend dependencies if needed."""
        frontend_dir = self.project_root / "frontend"
        package_json = frontend_dir / "package.json"
        node_modules = frontend_dir / "node_modules"

        if not package_json.exists():
            print("❌ frontend/package.json not found")
            return False

        if not node_modules.exists():
            print("📦 Installing frontend dependencies...")
            try:
                subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
                print("✅ Frontend dependencies installed")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install frontend dependencies: {e}")
                return False
        else:
            print("✅ Frontend dependencies already installed")

        return True

    def start_backend(self) -> bool:
        """Start the FastAPI backend server."""
        if self.frontend_only:
            return True

        print("🚀 Starting backend server...")

        try:
            # Set PYTHONPATH to include src directory
            env = os.environ.copy()
            env["PYTHONPATH"] = str(self.project_root / "src")

            self.backend_process = subprocess.Popen(
                [sys.executable, "-m", "tick_task.main"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            # Wait a bit for server to start
            time.sleep(2)

            # Check if process is still running
            if self.backend_process.poll() is None:
                print("✅ Backend server started on http://127.0.0.1:7000")
                return True
            else:
                stdout, stderr = self.backend_process.communicate()
                print(f"❌ Backend server failed to start")
                if stderr:
                    print(f"Error: {stderr}")
                return False

        except Exception as e:
            print(f"❌ Failed to start backend server: {e}")
            return False

    def start_frontend(self) -> bool:
        """Start the React/Vite frontend server."""
        if self.backend_only:
            return True

        print("🚀 Starting frontend server...")

        frontend_dir = self.project_root / "frontend"

        try:
            self.frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            # Wait a bit for server to start
            time.sleep(3)

            # Check if process is still running
            if self.frontend_process.poll() is None:
                print("✅ Frontend server started on http://localhost:5173")
                return True
            else:
                stdout, stderr = self.frontend_process.communicate()
                print(f"❌ Frontend server failed to start")
                if stderr:
                    print(f"Error: {stderr}")
                return False

        except Exception as e:
            print(f"❌ Failed to start frontend server: {e}")
            return False

    def wait_for_interrupt(self):
        """Wait for keyboard interrupt to shutdown servers."""
        try:
            print("\n🎯 Both servers are running!")
            print("📱 Frontend: http://localhost:5173")
            print("🔧 Backend API: http://127.0.0.1:7000/api/v1/")
            print("📚 API Docs: http://127.0.0.1:7000/docs")
            print("\nPress Ctrl+C to stop all servers...\n")

            while True:
                time.sleep(1)

                # Check if any process has died
                if self.backend_process and self.backend_process.poll() is not None:
                    print("❌ Backend server stopped unexpectedly")
                    break

                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("❌ Frontend server stopped unexpectedly")
                    break

        except KeyboardInterrupt:
            print("\n🛑 Shutting down servers...")

    def cleanup(self):
        """Clean up running processes."""
        processes = []

        if self.backend_process and self.backend_process.poll() is None:
            processes.append(("Backend", self.backend_process))

        if self.frontend_process and self.frontend_process.poll() is None:
            processes.append(("Frontend", self.frontend_process))

        for name, process in processes:
            print(f"🛑 Stopping {name} server...")
            try:
                process.terminate()
                # Wait up to 5 seconds for graceful shutdown
                process.wait(timeout=5)
                print(f"✅ {name} server stopped")
            except subprocess.TimeoutExpired:
                print(f"⚠️  {name} server didn't respond, force killing...")
                process.kill()
                process.wait()
                print(f"✅ {name} server force killed")

    def run(self) -> int:
        """Run the development servers."""
        print("🎯 FIN-tasks Development Server")
        print("=" * 40)

        # Check dependencies
        if not self.check_dependencies():
            return 1

        # Install frontend dependencies if needed
        if not self.frontend_only and not self.install_frontend_deps():
            return 1

        # Start servers
        success = True

        if not self.frontend_only and not self.start_backend():
            success = False

        if not self.backend_only and not self.start_frontend():
            success = False

        if not success:
            self.cleanup()
            return 1

        # Wait for interrupt
        try:
            self.wait_for_interrupt()
        finally:
            self.cleanup()

        print("👋 Development servers stopped. Goodbye!")
        return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Start FIN-tasks development servers")
    parser.add_argument(
        "--backend-only", action="store_true", help="Start only the backend server"
    )
    parser.add_argument(
        "--frontend-only", action="store_true", help="Start only the frontend server"
    )

    args = parser.parse_args()

    if args.backend_only and args.frontend_only:
        print("❌ Cannot specify both --backend-only and --frontend-only")
        return 1

    server = DevServer(backend_only=args.backend_only, frontend_only=args.frontend_only)

    return server.run()


if __name__ == "__main__":
    sys.exit(main())
