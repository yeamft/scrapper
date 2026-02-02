"""Create .env from .env.example if it doesn't exist. Edit .env with your values."""
import os
import shutil

project_dir = os.path.dirname(os.path.abspath(__file__))
example = os.path.join(project_dir, ".env.example")
env_file = os.path.join(project_dir, ".env")

if os.path.exists(env_file):
    print(".env already exists. Edit it to change values.")
else:
    if os.path.exists(example):
        shutil.copy(example, env_file)
        print("Created .env from .env.example. Edit .env and set your values.")
    else:
        print(".env.example not found.")
        exit(1)
