from setuptools import setup, find_packages

DESCRIPTION = "Marathi scripting language built upon Python 3"
LONG_DESCRIPTION = "Marathi scripting language built upon Python 3. All the keywords, functions, errors are written in Marathi language."

setup(
    name="bhashascript",
    version="1.0.0",
    include_package_data=True,
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "bhashascript = bhashascript.script:main",
        ],
    },
    author="Sapate Vaibhav",
    author_email="sapatevaibhav@duck.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/VaibhavCodeClub/BhashaScript",
    keywords=["marathi", "scripting", "language", "python"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
