"""
Setup Airflow: set AIRFLOW_HOME, create dags folder, initialize DB.
Run with: python setup_airflow.py
Use Python 3.10 or 3.11 (Airflow may not support 3.12+).
"""
import os
import sys
import subprocess

def main():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    airflow_home = os.path.join(project_dir, "airflow_home")
    dags_dir = os.path.join(airflow_home, "dags")

    os.environ["AIRFLOW_HOME"] = airflow_home
    os.makedirs(airflow_home, exist_ok=True)
    os.makedirs(dags_dir, exist_ok=True)
    os.makedirs(os.path.join(airflow_home, "logs"), exist_ok=True)
    os.makedirs(os.path.join(airflow_home, "plugins"), exist_ok=True)

    # Copy airflow.cfg so dags_folder = dags is used
    cfg_src = os.path.join(project_dir, "airflow.cfg")
    cfg_dst = os.path.join(airflow_home, "airflow.cfg")
    if os.path.exists(cfg_src):
        shutil.copy2(cfg_src, cfg_dst)
        print(f"Copied airflow.cfg to {cfg_dst}")

    # Copy DAG into airflow_home/dags so Airflow can load it
    import shutil
    src_dag = os.path.join(project_dir, "dags", "olx_scraper_dag.py")
    dst_dag = os.path.join(dags_dir, "olx_scraper_dag.py")
    if os.path.exists(src_dag):
        shutil.copy2(src_dag, dst_dag)
        print(f"Copied DAG to {dst_dag}")

    print(f"AIRFLOW_HOME={airflow_home}")
    print("Initializing Airflow database...")
    try:
        subprocess.run([sys.executable, "-m", "airflow", "db", "init"], check=True, cwd=project_dir)
        print("Airflow DB initialized.")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Create admin user if not exists
    try:
        subprocess.run([
            sys.executable, "-m", "airflow", "users", "create",
            "--username", "admin",
            "--firstname", "Admin",
            "--lastname", "User",
            "--role", "Admin",
            "--email", "admin@example.com",
            "--password", "admin",
        ], check=True, capture_output=True, cwd=project_dir)
        print("Admin user created (admin / admin)")
    except subprocess.CalledProcessError:
        pass  # User may already exist

    print("\nNext:")
    print("  1. start_airflow.bat   (webserver)")
    print("  2. start_scheduler.bat (scheduler)")
    print("  3. Open http://localhost:8080")

if __name__ == "__main__":
    main()
