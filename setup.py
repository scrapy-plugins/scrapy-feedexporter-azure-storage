from setuptools import find_packages, setup

setup(
    name="scrapy_azure_exporter",
    version="0.0.3",
    description="Scrapy Feed Exporter for Azure Storage",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "azure-storage-blob",
        "scrapy"
    ],
)