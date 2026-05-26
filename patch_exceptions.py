with open("binance50/src/binance50/core/exceptions.py", "r") as f:
    content = f.read()

exceptions = """
class MLDatasetError(Binance50Error):
    pass

class MLDatasetConfigError(MLDatasetError):
    pass

class MLFeatureSourceError(MLDatasetError):
    pass

class MLFeatureSelectionError(MLDatasetError):
    pass

class MLLabelError(MLDatasetError):
    pass

class MLLabelSpecError(MLDatasetError):
    pass

class MLSplitError(MLDatasetError):
    pass

class MLPreprocessingError(MLDatasetError):
    pass

class MLScalerError(MLDatasetError):
    pass

class MLAlignmentError(MLDatasetError):
    pass

class MLLeakageError(MLDatasetError):
    pass

class MLDatasetQualityError(MLDatasetError):
    pass

class MLDatasetRegistryError(MLDatasetError):
    pass

class MLDatasetCacheError(MLDatasetError):
    pass

class MLDatasetExportError(MLDatasetError):
    pass
"""

content += exceptions

with open("binance50/src/binance50/core/exceptions.py", "w") as f:
    f.write(content)
