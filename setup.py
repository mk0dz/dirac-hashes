from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dirac-hashes",
    version="0.1.0",
    author="mk0dz",
    author_email="Mukulpal108@hotmail.com",
    description="Quantum-resistant hash functions and post-quantum cryptography for blockchain",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mk0dz/dirac-hashes",
    project_urls={
        "Bug Tracker": "https://github.com/mk0dz/dirac-hashes/issues",
        "Documentation": "https://dirac-hashes.vercel.app/",
        "Source Code": "https://github.com/mk0dz/dirac-hashes",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.16.0",
        "scipy>=1.4.0",
        "qiskit>=0.20.0",
        "matplotlib>=3.0.0",
        "cryptography>=3.0.0",
        "pydantic>=1.5.1",
        "python-multipart>=0.0.5",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.5b2",
            "isort>=5.0.0",
            "mypy>=0.7",
        ],
        "api": [
            "fastapi>=0.70.0,<1.0.0",
            "uvicorn>=0.15.0,<1.0.0",
        ],
    },
) 