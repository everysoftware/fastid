def join_url_path(*parts: str) -> str:
    """Join application URL path components into one root-relative path."""
    segments = [segment.strip("/") for part in parts if part for segment in part.split("/") if segment]
    return f"/{'/'.join(segments)}"
