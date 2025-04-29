from setuptools import setup, find_packages

setup(
    name="masterspeak-ai",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0,<0.69.0",
        "uvicorn>=0.15.0,<0.16.0",
        "sqlmodel>=0.0.8",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-multipart>=0.0.5",
        "python-dotenv>=0.19.0",
        "jinja2>=3.0.1",
        "aiofiles>=0.7.0",
        "openai>=1.0.0",
        "pytest>=6.2.5",
        "httpx>=0.18.2",
        "sqlalchemy>=1.4.23",
        "pydantic>=1.8.2",
    ],
) 