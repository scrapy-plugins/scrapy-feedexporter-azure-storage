# Azure Exporter for Scrapy
scrapy_azure_exporter is a Python package which can be used in integration with scrapy for exporting feeds to Azure Storage.
## Description:
The scrapy_azure_exporter takes inspiration from the built-in feed exporters in scrapy. The built-in exporters doesn't have support for Azure yet.
So this scrapy_azure_exporter can be used whenever when we need the feeds to be exported to Azure Blob storage.

## Getting started:
### Installation:
```bash
> pip install git+https://github.com/scrapy-plugins/scrapy-feedexporter-azure-storage
```
### Usage:
* Add scrapy_azure_exporter to spider's settings.
```python
"FEED_STORAGES" : {'azure': 'scrapy_azure_exporter.AzureFeedStorage'}
```
* Provide authentication for Azure account via any of the three methods specified in the configuration section.
```python 
For example, "AZURE_CONNECTION_STRING": "Connection string for the Azure account"
```
* Add Azure URI of the location (the location where the feed needs to be exported) to the FEEDS dictionary. Reference: [FEEDS](https://docs.scrapy.org/en/latest/topics/feed-exports.html#feeds)

```python
"FEEDS": {
            "azure://<account_name>.blob.core.windows.net/<container_name>/<file_name.extension>":{
            "format": "json"
    }
}
```
### Configuration
All of the below parameters can be provided via spider's settings.
- Any of the following parameters can be provided for authentication. ([Ref](https://docs.microsoft.com/en-us/python/api/overview/azure/storage-blob-readme?view=azure-python)) 
  - `AZURE_CONNECTION_STRING` 
  - `AZURE_ACCOUNT_URL_WITH_SAS_TOKEN`
  - `AZURE_ACCOUNT_URL` & `AZURE_ACCOUNT_KEY` - If using this method, then both of these will be needed.
- `FEED_STORAGES` - For using our scrapy_azure_exporter. It's a scrapy built-in setting and we can provide values according to the scrapy docs. ([Ref](https://docs.scrapy.org/en/latest/topics/feed-exports.html#feed-storages)) 
- `FEEDS` - This is a scrapy setting and it should be a dict. It can be used to enable `scrapy_azure_exporter`. It's key should contain the Azure URI with the following format: `"azure://<account_name>.blob.core.windows.net/<container_name>/<file_name.extension>"`. The value of this key should be feed_options and this scrapy_azure_exporter supports the following feed_options. For more details on feed_options, see ([Docs](https://docs.scrapy.org/en/latest/topics/feed-exports.html#std-setting-FEEDS)). 
  - `overwrite` - Boolean value. It's worth mentioning that `overwrite=False` can only be provided when `blob_type="AppendBlob"`. For more info, see ([Understanding blob types](https://docs.microsoft.com/en-us/rest/api/storageservices/understanding-block-blobs--append-blobs--and-page-blobs))
  - `format` - Built-in scrapy feed formats ([Ref](https://docs.scrapy.org/en/latest/topics/feed-exports.html#topics-feed-format)) 
  - `blob_type` - The Azure Blob Types. This can be `"AppendBlob"`, `"BlockBlob"`, or `"PageBlob'`. Default is `"BlockBlob"`. ([Ref](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-blob-pageblob-overview?tabs=dotnet))
  