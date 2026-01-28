from setuptools import setup, find_packages

setup(
    name="vata-humanizer",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "vata = vata.cli:main",
        ],
    },
    install_requires=[
        "libcst>=1.0",
    ],
    author="Leroy H. Mason",
    author_email="your@email.com",
    description="Humanize AI code with soul",
    long_description="Make AI-generated code feel human with chaos transformations and soul scoring.",
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/vata-humanizer",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
