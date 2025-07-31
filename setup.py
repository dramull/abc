from setuptools import setup, find_packages

setup(
    name="multiagent-framework",
    version="1.0.0",
    description="A robust, modular multiagent framework using Kimi K2 and Qwen3 APIs",
    author="ABC Team",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.5.0",
        "streamlit>=1.28.0",
        "aiohttp>=3.9.0",
        "pyyaml>=6.0.0",
        "python-multipart>=0.0.6",
        "python-dotenv>=1.0.0",
        "rich>=13.7.0",
        "click>=8.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "httpx>=0.25.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "multiagent=multiagent_framework.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)