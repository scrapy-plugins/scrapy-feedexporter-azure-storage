import logging
from io import BytesIO

from azure.core.exceptions import ResourceExistsError
from twisted.internet import threads

from scrapy_azure_exporter.azure_exporter import AzureFeedStorage

logger = logging.getLogger(__name__)


class AzureFilesStore:
    AZURE_CONNECTION_STRING = None
    AZURE_ACCOUNT_URL_WITH_SAS_TOKEN = None
    AZURE_ACCOUNT_URL = None
    AZURE_ACCOUNT_KEY = None

    def __init__(self, uri):
        self.azure_feed = AzureFeedStorage(
            uri=uri,
            connection_string=self.AZURE_CONNECTION_STRING,
            account_url_with_sas_token=self.AZURE_ACCOUNT_URL_WITH_SAS_TOKEN,
            account_url=self.AZURE_ACCOUNT_URL,
            account_key=self.AZURE_ACCOUNT_KEY,
        )
        
    @classmethod
    def new(cls, settings):
        azure_fs = cls
        azure_fs.AZURE_CONNECTION_STRING = settings.get("AZURE_CONNECTION_STRING")
        azure_fs.AZURE_ACCOUNT_URL_WITH_SAS_TOKEN = settings.get("AZURE_ACCOUNT_URL_WITH_SAS_TOKEN")
        azure_fs.AZURE_ACCOUNT_URL = settings.get("AZURE_ACCOUNT_URL")
        azure_fs.AZURE_ACCOUNT_KEY = settings.get("AZURE_ACCOUNT_KEY")
        return azure_fs

    def stat_file(self, path, info):
        def _onsuccess(blob_client):
            if blob_client.exists():
                blob_properties = blob_client.get_blob_properties()
                checksum = blob_properties.etag.strip('"')
                last_modified = blob_properties.last_modified.timestamp()
                return {"checksum": checksum, "last_modified": last_modified}

            return {}

        return threads.deferToThread(
            self.azure_feed.blob_service_client.get_blob_client,
            self.azure_feed.container_name,
            path,
        ).addCallback(_onsuccess)

    def persist_file(self, path, buf, info, meta=None, headers=None):
        self.azure_feed.export_file_name = path

        try:
            self.azure_feed._store_in_thread(BytesIO(buf.getvalue()))
        except ResourceExistsError:
            pass
