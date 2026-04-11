def _includes_all(listing_text: str, reference_model: dict) -> bool:
    return all(
        any(keyword in listing_text for keyword in must_include_any)
        for must_include_any in reference_model["must_include"]
    )


def _find_match(listing_text: str, reference_models: list[dict]) -> dict | None:
    listing_text = listing_text.lower()
    for reference_model in reference_models:
        if any(
            [keyword in listing_text for keyword in reference_model["must_exclude"]]
        ):
            continue
        if _includes_all(listing_text, reference_model):
            return reference_model
    return None


def match_guitar_model(
    title: str, source_model: str | None, reference_models: list[dict]
) -> dict | None:
    matched = None
    if source_model:
        matched = _find_match(source_model, reference_models)
    if matched:
        return matched
    return _find_match(title, reference_models)
