from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dirac-hashes",
    version="0.1.0",
    author="Quantum Hash Team",
    author_email="example@example.com",
    description="Quantum-inspired hash functions and key generation for blockchain",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dirac-hashes",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "qiskit>=0.34.0",
        "matplotlib>=3.4.0",
        "cryptography>=3.4.8",
    ],
) 