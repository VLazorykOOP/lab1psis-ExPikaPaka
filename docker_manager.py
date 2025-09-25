import subprocess
import os
import time
import sys
from typing import Optional

class DockerManager:
    def __init__(self, project_path: str):
        """Initialize Docker Manager with project path."""
        self.project_path = project_path
        self.compose_file = os.path.join(project_path, 'docker-compose.yml')
        self.env_file = os.path.join(project_path, '.env')

    def run_command(self, command: str) -> tuple[int, str]:
        """Run a shell command and return the exit code and output."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            return result.returncode, result.stdout + result.stderr
        except subprocess.SubprocessError as e:
            return 1, str(e)

    def check_docker_running(self) -> bool:
        """Check if Docker daemon is running."""
        code, _ = self.run_command("docker info")
        return code == 0

    def start_containers(self) -> bool:
        """Start Docker containers."""
        print("Starting containers...")
        code, output = self.run_command("docker-compose up -d --build")
        print(output)
        return code == 0

    def stop_containers(self) -> bool:
        """Stop Docker containers."""
        print("Stopping containers...")
        code, output = self.run_command("docker-compose down")
        print(output)
        return code == 0

    def restart_containers(self) -> bool:
        """Restart Docker containers."""
        return self.stop_containers() and self.start_containers()

    def show_logs(self, tail: Optional[int] = None) -> None:
        """Show container logs."""
        cmd = "docker-compose logs"
        if tail:
            cmd += f" --tail={tail}"
        _, output = self.run_command(cmd)
        print(output)

    def show_status(self) -> None:
        """Show container status."""
        _, output = self.run_command("docker-compose ps")
        print(output)

def main():
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    manager = DockerManager(script_dir)

    if not manager.check_docker_running():
        print("Error: Docker is not running!")
        sys.exit(1)

    while True:
        print("\nDocker Manager Menu:")
        print("1. Start containers")
        print("2. Stop containers")
        print("3. Restart containers")
        print("4. Show container status")
        print("5. Show container logs")
        print("6. Exit")

        choice = input("\nEnter your choice (1-6): ")

        if choice == '1':
            manager.start_containers()
        elif choice == '2':
            manager.stop_containers()
        elif choice == '3':
            manager.restart_containers()
        elif choice == '4':
            manager.show_status()
        elif choice == '5':
            lines = input("Enter number of log lines to show (press Enter for all): ")
            tail = int(lines) if lines.isdigit() else None
            manager.show_logs(tail)
        elif choice == '6':
            print("Exiting...")
            break
        else:
            print("Invalid choice! Please try again.")

        time.sleep(1)  # Small delay to read output

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting due to user interrupt...")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)