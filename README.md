# Azure Exporter for Scrapy
[Scrapy feed export storage backend](https://doc.scrapy.org/en/latest/topics/feed-exports.html#storage-backends) for [Azure Storage](https://docs.microsoft.com/en-us/azure/storage/).

## Requirements
-  Python 3.8+

## Installation
```bash
pip install git+https://github.com/scrapy-plugins/scrapy-feedexporter-azure-storage
```
## Usage
* Add this storage backend to the [FEED_STORAGES](https://docs.scrapy.org/en/latest/topics/feed-exports.html#std-setting-FEED_STORAGES) Scrapy setting. For example:
    ```python
    # settings.py
    FEED_STORAGES = {'azure': 'scrapy_azure_exporter.AzureFeedStorage'}
    ```
* Configure [authentication](https://docs.microsoft.com/en-us/python/api/overview/azure/storage-blob-readme?view=azure-python) via any of the following settings:
  - `AZURE_CONNECTION_STRING` 
  - `AZURE_ACCOUNT_URL_WITH_SAS_TOKEN`
  - `AZURE_ACCOUNT_URL` & `AZURE_ACCOUNT_KEY` - If using this method, specify both of them.
  
  For example,
  ```python 
  AZURE_ACCOUNT_URL = "https://<your-storage-account-name>.blob.core.windows.net/"
  AZURE_ACCOUNT_KEY = "Account key for the Azure account"
    ```
* Configure in the [FEEDS](https://docs.scrapy.org/en/latest/topics/feed-exports.html#feeds) Scrapy setting the Azure URI where the feed needs to be exported.

    ```python
    FEEDS = {
        "azure://<account_name>.blob.core.windows.net/<container_name>/<file_name.extension>": {
            "format": "json"
        }
    }
    ```
## Write mode and blob type
The `overwrite`
[feed option](https://docs.scrapy.org/en/latest/topics/feed-exports.html#feed-options)
is `False` by default when using this feed export storage backend.
An extra feed option is also provided, `blob_type`, which can be `"BlockBlob"` 
(default) or `"AppendBlob"`. See 
[Understanding blob types](https://docs.microsoft.com/en-us/rest/api/storageservices/understanding-block-blobs--append-blobs--and-page-blobs).
The feed options `overwrite` and `blob_type` can be combined to set the write
mode of the feed export:
- `overwrite=False` and `blob_type="BlockBlob"` create the blob if it does not 
  exist, and fail if it exists.
- `overwrite=False` and `blob_type="AppendBlob"` append to the blob if it 
  exists and it is an `AppendBlob`, and create it otherwise. 
- `overwrite=True` overwrites the blob, even if it exists. The `blob_type` must
  match that of the target blob.

## Media pipeline usage

Create a custom pipeline for [Scrapy media pipelines](https://docs.scrapy.org/en/latest/topics/media-pipeline.html) and be able to use Azure Blob Storage.

```python
from scrapy.pipelines.files import FilesPipeline as FSPipeline
from scrapy_azure_exporter.azure_store import AzureFilesStore


class FilesPipeline(FSPipeline):
    @classmethod
    def from_settings(cls, settings):
        azure_store = AzureFilesStore
        azure_store.AZURE_CONNECTION_STRING = settings.get("AZURE_CONNECTION_STRING")
        azure_store.AZURE_ACCOUNT_URL_WITH_SAS_TOKEN = settings.get("AZURE_ACCOUNT_URL_WITH_SAS_TOKEN")
        azure_store.AZURE_ACCOUNT_URL = settings.get("AZURE_ACCOUNT_URL")
        azure_store.AZURE_ACCOUNT_KEY = settings.get("AZURE_ACCOUNT_KEY")

        cls.STORE_SCHEMES.update({"azure": azure_store})
        return cls(settings.get("FILES_STORE"), settings=settings)
```

Add the pipeline to Scrapy:

```python
ITEM_PIPELINES = {
    "path.to.FilesPipeline": 1,
}
```

## Azurite usage

You can use [Azurite](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azurite?tabs=visual-studio) as a storage emulator for Azure Blob Storage
and test your application locally.

```python
# NOTE: The "http" schema is necessary to compatibility with Azurite
cls.STORE_SCHEMES.update({"azure": azure_store, "http": azure_store})
```

And finally run your Scrapy project as it is usually done for FilesPipeline or ImagesPipeline.
