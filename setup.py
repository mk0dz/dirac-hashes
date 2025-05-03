#!/usr/bin/env python3
"""
Setup script for Dirac Hashes - Quantum-Resistant Cryptographic Library.

This script builds the C extension modules and installs the package.
"""

from setuptools import setup, find_packages, Extension
import os
import sys
import platform

# Detect if we're on x86 architecture to enable SSE/AVX optimizations
is_x86 = platform.machine().lower() in ['x86_64', 'amd64', 'i386', 'i686']

# Optimization flags
if is_x86:
    # Enable SSE2/SSE4/AVX2 for x86 architectures
    extra_compile_args = ['-O3', '-march=native', '-mtune=native']
    if sys.platform != 'darwin':  # macOS has different compiler flags
        extra_compile_args.extend(['-msse2', '-msse4', '-mavx2'])
else:
    # Generic optimizations for other architectures
    extra_compile_args = ['-O3']

# Define the C extension module
optimized_core = Extension(
    'src.quantum_hash.core.optimized_core',
    sources=['src/quantum_hash/core/optimized_core.c'],
    extra_compile_args=extra_compile_args,
    extra_link_args=['-O3'],
    include_dirs=[],
)

# Hybrid hash function extension
hybrid_core = Extension(
    'src.quantum_hash.core.hybrid_core',
    sources=['src/quantum_hash/core/hybrid_core.c'],
    extra_compile_args=extra_compile_args,
    extra_link_args=['-O3'],
)

# Check for optional packages
requirements = [
    'numpy>=1.18.0',
    'scipy>=1.4.0',
]

try:
    import numba
    has_numba = True
except ImportError:
    has_numba = False
    requirements.append('numba>=0.50.0')

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dirac-hashes',
    version='1.0.0',
    description='Quantum-Resistant Cryptographic Hash Functions',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/dirac-hashes',
    packages=find_packages(),
    install_requires=requirements,
    ext_modules=[optimized_core],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: C',
        'Topic :: Security :: Cryptography',
    ],
    python_requires='>=3.7',
    keywords='cryptography, post-quantum, hash-functions, signatures',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/dirac-hashes/issues',
        'Source': 'https://github.com/yourusername/dirac-hashes',
    },
) 