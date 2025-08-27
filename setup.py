import os
from setuptools import setup, find_packages

# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "burpr",
    version = "0.3.0",
    author = "Krystian Bajno",
    author_email = "krystian.bajno@gmail.com",
    description = ("A Burp Suite request parser, used for aid in assessing application security functionality."),
    license = "MIT",
    long_description_content_type='text/markdown',
    keywords = "burp suite burpsuite request parser security testing http http2",
    url = "https://github.com/krystianbajno/burpr",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "httpx[http2]>=0.23.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov",
        ]
    },
    long_description=read('README.md'),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.7',
)