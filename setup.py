from setuptools import setup, find_packages

setup(
    name="python3-ptock",
    version="1.1.0",
    packages=find_packages(),
    description="A digital clock made in Python for the terminal, inspired by tty-clock and tock.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Andre Ribeiro",
    author_email="andre.ribeiro.srs@gmail.com",
    url="https://github.com/andrerclaudio/python3-ptock",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Linux",
    ],
    python_requires=">=3.12.7",
    entry_points={
        "console_scripts": [
            "ptock=ptock.main:main",  # Ensure this points to your main function
        ],
    },
)
