from setuptools import setup, find_packages

project_description = "Deploy infrastructure as code via polling"

# Read the requirements from the requirements.txt file
with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

# Read the description from the markdown file
with open('README.md', 'r') as f:
    description = f.read()

setup(
    name="pyiaacsync",
    version="0.2",
    packages=find_packages(),
    install_requires=requirements,
    description=project_description,
    long_description=description,
    long_description_content_type="text/markdown"
)