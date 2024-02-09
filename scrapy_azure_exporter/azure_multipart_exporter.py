import io

from azure.storage.blob import BlobServiceClient
from scrapy_azure_exporter import AzureFeedStorage


class AzureBlobWriter(io.IOBase):
    """
    A synchronous writer for Azure blob using Multipart Uploads.
    """

    def __init__(
        self,
        account_url_with_sas_token,
        container_name,
        blob_name,
        max_block_size=2 * 1024 * 1024,
    ):
        self.block_ids = []
        self.total_size = 0

        self.account_url_with_sas_token = account_url_with_sas_token
        self.container_name = container_name
        self.blob_name = blob_name
        self.max_block_size = max_block_size

        self.blob_service_client = BlobServiceClient(account_url=account_url_with_sas_token)
        self.blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    def writable(self):
        return True

    def write(self, data):
        if not data:
            return 0

        start = 0
        end = len(data)
        while start < end:
            chunk_size = min(self.max_block_size, end - start)
            chunk = data[start : start + chunk_size]
            start += chunk_size

            block_id = f"{len(self.block_ids):08d}"
            self.blob_client.stage_block(block_id, chunk)
            self.block_ids.append(block_id)
            self.total_size += len(chunk)

        return len(data)

    def close(self):
        self.blob_client.commit_block_list(self.block_ids)


class AzureMultipartFeedStorage(AzureFeedStorage):
    DEFAULT_BUFFER_SIZE = 104857600  # 100 MiB

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
        super(AzureMultipartFeedStorage, self).__init__(
            uri=uri,
            connection_string=connection_string,
            account_url_with_sas_token=account_url_with_sas_token,
            account_url=account_url,
            account_key=account_key,
            feed_options=feed_options,
        )
        self.writer = AzureBlobWriter(
            account_url_with_sas_token,
            self.container_name,
            self.export_file_name,
            max_block_size=self.DEFAULT_BUFFER_SIZE,
        )

    def open(self, spider):
        """
        Create a Buffered Writer using the AzureBlobWriter to optimize data upload.

        Default buffer size is 100 MiB as defined in `DEFAULT_BUFFER_SIZE`
        """
        return io.BufferedWriter(self.writer, self.DEFAULT_BUFFER_SIZE)

    def _store_in_thread(self, buffered_file):
        """
        Flush/close buffered data and complete the Multipart Upload.
        """
        buffered_file.close()
        self.writer.close()
