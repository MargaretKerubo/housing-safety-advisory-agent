from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="housing-safety-advisory-agent",
    version="0.1.0",
    author="Housing Safety Team",
    author_email="team@example.com",
    description="An AI-powered decision-support agent that helps users evaluate housing options by reasoning over safety-related trade-offs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-repo/housing-safety-advisory-agent",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "housing-agent=main:main",
        ],
    },
)