from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError
import typing
from scrapy.exceptions import NotConfigured
from scrapy.extensions.feedexport import BlockingFeedStorage
import logging

"""The pipeline for adding a file to Azure Blob"""


class AzureFeedExporter(BlockingFeedStorage):

    def __init__(self, container_name, blob_service_client, azure_export_filename):
        self.container_name = container_name
        self.blob_service_client = blob_service_client
        self.azure_export_filename = azure_export_filename

    @classmethod
    def from_crawler(cls, crawler) -> typing.Any:
        container_name = crawler.settings.get("CONTAINER_NAME")
        connection_string = crawler.settings.get("CONNECTION_STRING")
        azure_export_filename = crawler.settings.get("AZURE_EXPORT_FILENAME")

        try:
            blob_service_client = BlobServiceClient.from_connection_string(conn_str=connection_string)
        except ValueError as e:
            raise NotConfigured(
                f"Could not connect to Azure Client: {e}"
            )
        return cls(
            container_name=container_name,
            blob_service_client=blob_service_client,
            azure_export_filename=azure_export_filename
        )

    def _store_in_thread(self, file):
        file.seek(0)
        try:
            blob_client = self.blob_service_client.get_blob_client(self.container_name, self.azure_export_filename)
        except ResourceNotFoundError as e:
            logging.error(f"Container doesn't exist: {e}")
            return

        with open(file, "rb") as data:
            blob_client.upload_blob(data)
