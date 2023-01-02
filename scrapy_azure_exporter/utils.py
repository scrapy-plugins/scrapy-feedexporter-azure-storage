from scrapy_azure_exporter import AzureFeedStorage
from azure.core.exceptions import ResourceExistsError
from scrapy.pipelines.files import FilesPipeline
from scrapy.utils.project import get_project_settings

settings = get_project_settings()

class AzureFilesStore():
    def __init__(self,uri):
        self.azure_feed = AzureFeedStorage(
            uri = uri,
            connection_string = settings.get('AZURE_CONNECTION_STRING',False),
            account_url_with_sas_token = settings.get('AZURE_ACCOUNT_URL_WITH_SAS_TOKEN', False),
            account_url = settings.get('AZURE_ACCOUNT_URL',False),
            account_key = settings.get('AZURE_ACCOUNT_KEY',False)
        )

        self.basename = self.azure_feed.export_file_name[:]

    def persist_file(self, path, buf, info, meta=None, headers= None):
        self.azure_feed.export_file_name = os.path.join(self.basename,path)
        try:
            self.azure_feed._store_in_thread(BytesIO(buf.getvalue()))
        except ResourceExistsError:
            pass


FilesPipeline.STORE_SCHEMES.update({
    'azure': AzureFilesStore
})
