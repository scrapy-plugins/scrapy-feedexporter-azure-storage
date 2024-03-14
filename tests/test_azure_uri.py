from scrapy_azure_exporter.azure_store import AzureFeedStorage


def test_azure_uri():
    uri = "azure://example.blob.core.windows.net/container/file.ext"
    extracted_params = AzureFeedStorage.parse_azure_uri(AzureFeedStorage, uri=uri)

    assert isinstance(extracted_params, dict)
    assert extracted_params["container_name"] == "container"
    assert extracted_params["export_file_name"] == "file.ext"


def test_azurite_uri():
    uri = "http://127.0.0.1:10000/devstoreaccount1/container/file.ext"
    extracted_params = AzureFeedStorage.parse_azure_uri(AzureFeedStorage, uri=uri)

    assert isinstance(extracted_params, dict)
    assert extracted_params["container_name"] == "container"
    assert extracted_params["export_file_name"] == "file.ext"
