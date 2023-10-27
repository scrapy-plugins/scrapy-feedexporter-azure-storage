from scrapy_azure_exporter.azure_store import AzureFilesStore
from scrapy.pipelines.files import FilesPipeline
from scrapy.pipelines.images import ImagesPipeline


class AzurePipelineMixin:
    @classmethod
    def from_settings(cls, settings):
        pipeline = super().from_settings(settings)
        pipeline.STORE_SCHEMES.update(
            {
                "azure": AzureFilesStore.new(settings),
                "http": AzureFilesStore.new(settings),
            }
        )
        return pipeline


class AzureFilesPipeline(AzurePipelineMixin, FilesPipeline):
    pass


class AzureImagesPipeline(AzurePipelineMixin, ImagesPipeline):
    pass
