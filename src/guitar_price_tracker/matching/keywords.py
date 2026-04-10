def _includes_all(title_or_source_model: str, reference_model: dict) -> bool:
    return all(
        any(keyword in title_or_source_model for keyword in must_include_any)
        for must_include_any in reference_model["must_include"]
    )


def _match_model(source_model: str, reference_models: list[dict]) -> dict | None:
    source_model = source_model.lower()
    for reference_model in reference_models:
        if _includes_all(source_model, reference_model):
            return reference_model
    return None


def _match_title(title: str, reference_models: list[dict]) -> dict | None:
    title = title.lower()
    for reference_model in reference_models:
        if any([keyword in title for keyword in reference_model["must_exclude"]]):
            continue
        if _includes_all(title, reference_model):
            return reference_model
    return None


def match_guitar_model(
    title: str, source_model: str | None, reference_models: list[dict]
) -> dict | None:
    matched = None
    if source_model:
        matched = _match_model(source_model, reference_models)
    if matched:
        return matched
    return _match_title(title, reference_models)
