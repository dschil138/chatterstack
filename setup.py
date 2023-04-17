from setuptools import setup, find_packages

setup(
    name="chatterstack",
    version="0.1.0",
    description="A custom class to manage a list of dictionaries representing a conversation, specifically for ChatGPT model gpt-3.5-turbo and gpt-4.",
    author="David Schiller",
    url="https://github.com/dschil138/chatterstack",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
)
