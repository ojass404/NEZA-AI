"""Semantic-segmentation availability guard for NEZA AI."""


class UNetSegmentor:
    """Prevent unverified segmentation weights from being used."""

    def __init__(self, model_path: str | None = None) -> None:
        raise RuntimeError(
            "Semantic segmentation is currently disabled. "
            "No verified U-Net model has been trained and evaluated. "
            "Do not present generated masks as valid segmentation."
        )
