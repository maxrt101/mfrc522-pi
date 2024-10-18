import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mfrc522pi",
    version="0.1.0",
    author="maxrtx",
    author_email="maxrt101@git",
    description="Setup for mfrc522pi",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/maxrt101/mfrc522-pi",
    packages=['mfrc522pi'],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.9',
)
