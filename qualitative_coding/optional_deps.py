import importlib
from qualitative_coding.exceptions import QCError

AI_EXTRA = "ai"

def import_ai_dependency(module_name, feature):
    """Imports an optional AI dependency (spacy, openai, scikit-learn,
    krippendorff), raising a QCError with installation instructions if
    it is not installed.
    """
    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        raise QCError(
            f"{feature} requires the optional '{AI_EXTRA}' dependency group, "
            f"which is not installed.\nInstall it with:\n"
            f"  uv sync --extra {AI_EXTRA}\n"
            f"or:\n"
            f"  pip install qualitative-coding[{AI_EXTRA}]"
        ) from e
