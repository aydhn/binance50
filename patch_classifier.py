with open("binance50/src/binance50/core/error_classifier.py", "r") as f:
    content = f.read()

import_statement = """
    MLDatasetError,
    MLDatasetConfigError,
    MLFeatureSourceError,
    MLFeatureSelectionError,
    MLLabelError,
    MLLabelSpecError,
    MLSplitError,
    MLPreprocessingError,
    MLScalerError,
    MLAlignmentError,
    MLLeakageError,
    MLDatasetQualityError,
    MLDatasetRegistryError,
    MLDatasetCacheError,
    MLDatasetExportError,
"""

content = content.replace("    StreamStaleEventError,\n)", import_statement + "    StreamStaleEventError,\n)")

classifier_logic = """
    if "label in features" in msg_lower:
        return MLLeakageError
    if "future column in features" in msg_lower:
        return MLLeakageError
    if "target in features" in msg_lower:
        return MLLeakageError
    if "global scaler fit" in msg_lower:
        return MLPreprocessingError
    if "validation fit" in msg_lower:
        return MLPreprocessingError
    if "test fit" in msg_lower:
        return MLPreprocessingError
    if "split overlap" in msg_lower:
        return MLSplitError
    if "forward alignment" in msg_lower:
        return MLAlignmentError
    if "missing labels" in msg_lower:
        return MLLabelError
    if "class imbalance" in msg_lower:
        return MLDatasetQualityError
    if "no features" in msg_lower:
        return MLFeatureSelectionError
"""

content = content.replace("    if \"no trials generated\" in msg_lower:", classifier_logic + "\n    if \"no trials generated\" in msg_lower:")

with open("binance50/src/binance50/core/error_classifier.py", "w") as f:
    f.write(content)
