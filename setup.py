from setuptools import setup, find_packages

# Read the requirements from the requirements.txt file
with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

# Read the description from the markdown file
with open('README.md', 'r') as f:
    description = f.read().splitlines()

setup(
    name="pyiaacsync",
    version="0.2",
    packages=find_packages(),
    install_requires=requirements,
    long_description=description,
    long_description_content_type="text/markdown"
)