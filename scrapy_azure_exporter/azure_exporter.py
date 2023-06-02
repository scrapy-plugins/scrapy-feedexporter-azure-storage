import logging
import os
import typing
from urllib.parse import urlparse

from azure.core.exceptions import AzureError
from azure.storage.blob import BlobServiceClient
from azure.storage.blob._models import BlobType
from scrapy.exceptions import NotConfigured
from scrapy.extensions.feedexport import BlockingFeedStorage

logger = logging.getLogger(__name__)


class AzureFeedStorage(BlockingFeedStorage):
    """This class will be used for exporting files to Azure Blob Storage"""

    def __init__(
        self,
        uri,
        connection_string,
        account_url_with_sas_token,
        account_url,
        account_key,
        *,
        feed_options=None,
    ):
        if feed_options is None:
            feed_options = {}

        self.connection_string = connection_string
        self.account_url_with_sas_token = account_url_with_sas_token
        self.account_url = account_url
        self.account_key = account_key
        self.overwrite = feed_options.get("overwrite", False)
        self.blob_type = feed_options.get("blob_type", "BlockBlob")

        if self.blob_type not in (BlobType.BLOCKBLOB, BlobType.APPENDBLOB):
            raise NotConfigured("Please specify the correct blob_type")

        extracted_params = self.parse_azure_uri(uri)

        if not extracted_params:
            raise NotConfigured(
                "Please provide URI according to this format,"
                "azure://<account_name>.blob.core.windows.net/<container_name>/<file_name.extension>"
            )

        self.container_name = extracted_params.get("container_name")
        self.export_file_name = extracted_params.get("export_file_name")

        try:
            if account_url and account_key:
                self.blob_service_client = BlobServiceClient(
                    account_url=account_url, credential=account_key
                )
            elif connection_string:
                self.blob_service_client = BlobServiceClient.from_connection_string(
                    conn_str=connection_string
                )
            elif account_url_with_sas_token:
                self.blob_service_client = BlobServiceClient(
                    account_url=account_url_with_sas_token
                )
            else:
                raise NotConfigured("Please provide valid credentials.")
        except AzureError as e:
            raise NotConfigured(e)

    @classmethod
    def from_crawler(cls, crawler, uri, *, feed_options=None) -> typing.Any:
        return cls(
            uri=uri,
            connection_string=crawler.settings.get("AZURE_CONNECTION_STRING"),
            account_url_with_sas_token=crawler.settings.get(
                "AZURE_ACCOUNT_URL_WITH_SAS_TOKEN"
            ),
            account_url=crawler.settings.get("AZURE_ACCOUNT_URL"),
            account_key=crawler.settings.get("AZURE_ACCOUNT_KEY"),
            feed_options=feed_options,
        )

    def _store_in_thread(self, file):
        file.seek(0)

        self.blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, blob=self.export_file_name
        )
        _ = self.blob_client.upload_blob(
            file, blob_type=self.blob_type, overwrite=self.overwrite
        )

        file.close()

    def parse_azure_uri(cls, uri):
        "Takes in uri and extracts container name and filename"
        extracted_params = {}

        try:
            parsed_url = urlparse(uri)
            # split till 2nd occurrence of slash,
            # so we can get container name and file name separated.
            # NOTE: This workaround is necessary for compatibility with
            # Azurite that have the path in the format
            # `/<account_name>/<container_name>/<filename.ext>`
            splitted = parsed_url.path.split("/", 2)
            container_name = splitted[1]
            file_name = splitted[2]

            if parsed_url.scheme == "http":
                splitted = parsed_url.path.split("/", 3)
                container_name = splitted[2]
                file_name = None

                if len(splitted) > 3:
                    file_name = splitted[3]

            # NOTE: In case `file_name` is `None` it should be
            # a valid condition, since it is assumed that the
            # user wants to use the container to save all files
            # from a pipeline
            if not container_name or not os.path.basename(parsed_url.path):
                return

            extracted_params["container_name"] = container_name
            extracted_params["export_file_name"] = file_name
            return extracted_params
        except IndexError as e:
            logger.error(e)
            return
        except Exception as e:
            logger.error(e)
            return
