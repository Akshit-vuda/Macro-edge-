"""
Prefect Worker Orchestrator.

Starts a background Prefect server, deploys a trivial flow, triggers a flow run,
and starts the Prefect agent to execute it.
"""

import os
import subprocess
import sys
import time
import urllib.request
from typing import Any
from prefect import flow


@flow
def trivial_flow() -> str:
    """
    A trivial flow to verify that the Prefect agent/worker is running properly.
    
    Returns:
        str: Status message indicating success.
    """
    print("Trivial flow executed successfully!")
    return "Success"


def start_prefect_server() -> subprocess.Popen[Any]:
    """
    Starts the Prefect server in a background process.
    
    Returns:
        subprocess.Popen: The started server process.
    """
    print("Starting Prefect server...")
    server_process = subprocess.Popen(
        ["prefect", "server", "start", "--host", "0.0.0.0", "--port", "4200"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return server_process


def wait_for_server(url: str, timeout_seconds: int = 30) -> None:
    """
    Waits for the Prefect server health endpoint to respond successfully.
    
    Args:
        url (str): The health check API URL.
        timeout_seconds (int): Maximum seconds to wait.
        
    Raises:
        RuntimeError: If the server does not become healthy within the timeout.
    """
    for _ in range(timeout_seconds):
        try:
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    print("Prefect server is healthy!")
                    return
        except Exception:
            time.sleep(1)
            
    raise RuntimeError(f"Prefect server failed to start at {url} within {timeout_seconds}s")


def deploy_and_run_flow() -> None:
    """
    Deploys the trivial flow to the local Prefect server and triggers a flow run.
    """
    print("Deploying trivial flow...")
    deployment = trivial_flow.to_deployment(
        name="trivial-deployment",
        work_queue_name="default"
    )
    deployment.apply()
    
    print("Triggering trivial flow run...")
    subprocess.run([
        "prefect", "deployment", "run", "trivial-flow/trivial-deployment"
    ], check=True)


def start_agent() -> None:
    """
    Starts the Prefect agent to process runs on the 'default' queue.
    """
    print("Starting Prefect agent...")
    subprocess.run([
        "prefect", "agent", "start", "-q", "default"
    ], check=True)


def main() -> None:
    """
    Main entry point for starting the Prefect stack and agent.
    """
    # Determine DB path dynamically to avoid hardcoded absolute paths
    db_path = "/app/data/prefect.db"
    if not os.path.exists("/app/data"):
        os.makedirs("./data", exist_ok=True)
        db_path = os.path.abspath("./data/prefect.db")
        
    # Force Prefect to use our internal SQLite DB
    os.environ["PREFECT_API_DATABASE_CONNECTION_URL"] = f"sqlite+aiosqlite:///{db_path}"
    
    # Configure API URL to local server
    os.environ["PREFECT_API_URL"] = "http://localhost:4200/api"
    
    server_process = start_prefect_server()
    
    try:
        wait_for_server("http://localhost:4200/api/health")
        deploy_and_run_flow()
        start_agent()
    except Exception as e:
        print(f"Error occurred: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        print("Terminating Prefect server process...")
        server_process.terminate()
        server_process.wait()


if __name__ == "__main__":
    main()
