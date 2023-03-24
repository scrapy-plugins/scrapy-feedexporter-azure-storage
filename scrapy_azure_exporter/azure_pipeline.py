import logging

from scrapy.pipelines.files import FilesPipeline as FSPipeline

from scrapy_azure_exporter.azure_store import AzureFilesStore

logger = logging.getLogger(__name__)


class FilesPipeline(FSPipeline):
    @classmethod
    def from_settings(cls, settings):
        azure_store = AzureFilesStore
        azure_store.AZURE_CONNECTION_STRING = settings.get("AZURE_CONNECTION_STRING")
        azure_store.AZURE_ACCOUNT_URL_WITH_SAS_TOKEN = settings.get(
            "AZURE_ACCOUNT_URL_WITH_SAS_TOKEN"
        )
        azure_store.AZURE_ACCOUNT_URL = settings.get("AZURE_ACCOUNT_URL")
        azure_store.AZURE_ACCOUNT_KEY = settings.get("AZURE_ACCOUNT_KEY")

        # NOTE: The "http" schema is necessary to compatibility with Azurite
        cls.STORE_SCHEMES.update({"azure": azure_store, "http": azure_store})
        return cls(settings.get("FILES_STORE"), settings=settings)
