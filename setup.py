from setuptools import setup, find_packages # find_packages को import करें
import os

# --- 1. Dependencies List ---
REQUIRED_PACKAGES = [
    'click',
    'ruamel.yaml', 
]

# --- 2. README.md Load ---
try:
    with open('README.md', encoding='utf-8') as f:
        README_content = f.read()
except FileNotFoundError:
    README_content = ''

setup(
    name='envsanitycheck',
    version='1.0.3', # Updated version
    packages=find_packages(), 
    # 3. Dependencies
    install_requires=REQUIRED_PACKAGES,
    
    # 4. Metadata
    author='Lokesh Kumar',
    description='A robust CLI tool for validating project environment variables (.env files) with type checking.',
    long_description=README_content,
    long_description_content_type='text/markdown',
    url='https://github.com/trmxvibs/EnvSanityCheck',
    license='MIT',
    
    # 5. Classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Utilities',
    ],
    
    # 6. Entry Point
    entry_points={
        'console_scripts': [
            'envcheck = envsanitycheck.cli:envsanitycheck',
        ],
    },
)
