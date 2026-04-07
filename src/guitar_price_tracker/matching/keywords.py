def _includes_all(source_title_or_model: str, model: dict) -> bool:
    return all(
        any(keyword in source_title_or_model for keyword in must_include_any)
        for must_include_any in model["must_include"]
    )

def _match_model(source_model: str, reference_models: list[dict]) -> dict | None:
    source_model = source_model.lower()
    for model in reference_models:
        if _includes_all(source_model, model):
            return model
    return None

def _match_title(source_title: str, reference_models: list[dict]) -> dict | None:
    source_title = source_title.lower()
    for model in reference_models:
        if any([keyword in source_title for keyword in model["must_exclude"]]):
            continue
        if _includes_all(source_title, model):
            return model
    return None

def match_guitar_model(
        source_title: str, 
        source_model: str | None, 
        reference_models: list[dict]
) -> dict | None:
    matched = None
    if source_model:
        matched = _match_model(source_model, reference_models)
    if matched:
        return matched
    return _match_title(source_title, reference_models)