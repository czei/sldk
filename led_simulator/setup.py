from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="led_simulator",
    version="0.1.0",
    author="LED Simulator Contributors",
    description="LED matrix display simulator for CircuitPython development",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/led_simulator",
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Embedded Systems",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pygame>=2.0.0",
        "pillow>=8.0.0",
        "numpy>=1.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
    },
    package_data={
        "led_simulator": ["fonts/*.bdf"],
    },
    include_package_data=True,
    license="Apache-2.0",
    keywords="led matrix display simulator circuitpython adafruit displayio",
)