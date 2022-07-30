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
## Supported feed options
 - The below feed options are supported. See their usage and details [here](https://docs.scrapy.org/en/latest/topics/feed-exports.html#feeds).
   - format
   - encoding
   - fields
   - item_classes
   - item_filter
   - indent
   - item_export_kwargs
   - overwrite
   - store_empty
   - uri_params
   - batch_item_count
 - The following ones are specific to this storage backend.
   - `overwrite` - Default is `False`
   - `blob_type` - The Azure Blob Types. This can be `"AppendBlob"` or `"BlockBlob"`. Default is `"BlockBlob"`. (See [Understanding blob types](https://docs.microsoft.com/en-us/rest/api/storageservices/understanding-block-blobs--append-blobs--and-page-blobs))
   - The feed_options `overwrite` and `blob_type` can be used in combination to serve different modes.
     - `overwrite=False` and `blob_type="BlockBlob"`
       - Create the blob if it does not exist. If it already exists, the `azure.core.exceptions.ResourceExistsError` exception will be raised.
     - `overwrite=False` and `blob_type="AppendBlob"`
       - Append the blob if it exists (The blob to which you're appending should be an AppendBlob). If it doesn't exist, create it. 
     - `overwrite=True` and any `blob_type`
       - overwrite the blob, even if it exists. However, blobs can only be overwritten if the blob_type remains same. For example. you can overwrite a `BlockBlob` by `BlockBlob` only.
 - The `postprocessing` feed option is currently unsupported.