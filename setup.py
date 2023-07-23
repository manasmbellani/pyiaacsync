import subprocess
from setuptools import setup, find_packages

project_description = "Deploy infrastructure as code via polling"

def get_git_remote_url():
    try:
        remote_url = subprocess.check_output(["git", "config", "--get", "remote.origin.url"])
        return remote_url.strip().decode("utf-8")
    except Exception:
        return None

# Read the requirements from the requirements.txt file
with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

# Read the description from the markdown file
with open('README.md', 'r') as f:
    description = f.read()

setup(
    name="pyiaacsync",
    version="0.6",
    packages=find_packages(),
    install_requires=requirements,
    description=project_description,
    long_description=description,
    long_description_content_type="text/markdown",
    url=get_git_remote_url()
)