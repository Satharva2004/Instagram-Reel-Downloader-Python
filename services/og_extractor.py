import os
from urllib.parse import urlparse, urlunparse

import requests
from bs4 import BeautifulSoup


def remove_query_from_url(url: str) -> str:
    parsed = urlparse(url)
    sanitized = parsed._replace(query="", fragment="")
    return urlunparse(sanitized)


def _extract_download_link(og_tags: dict) -> str | None:
    preferred_keys = [
        "og:video:secure_url",
        "og:video:url",
        "og:video",
    ]
    for key in preferred_keys:
        value = og_tags.get(key)
        if value:
            return value
    return None


def _looks_like_media_url(value: str) -> bool:
    lowered = value.lower()
    return lowered.startswith("http") and (
        lowered.endswith(".mp4")
        or "cdninstagram" in lowered
        or "fbcdn" in lowered
    )


def _extract_media_url_from_payload(payload) -> str | None:
    if isinstance(payload, str):
        if _looks_like_media_url(payload):
            return payload
        return None
    if isinstance(payload, dict):
        for candidate_key in [
            "download",
            "download_url",
            "video",
            "video_url",
            "url",
            "hd",
            "mp4",
        ]:
            if candidate_key in payload:
                link = _extract_media_url_from_payload(payload[candidate_key])
                if link:
                    return link
        for value in payload.values():
            link = _extract_media_url_from_payload(value)
            if link:
                return link
    if isinstance(payload, (list, tuple)):
        for item in payload:
            link = _extract_media_url_from_payload(item)
            if link:
                return link
    return None


def _fetch_download_link_via_rapidapi(clean_url: str) -> str | None:
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        raise RuntimeError("RAPIDAPI_KEY environment variable is not set")

    rapidapi_host = os.getenv(
        "RAPIDAPI_HOST",
        "instagram-downloader-download-instagram-stories-videos4.p.rapidapi.com",
    )

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": rapidapi_host,
    }
    params = {"url": clean_url}
    response = requests.get(
        f"https://{rapidapi_host}/convert",
        headers=headers,
        params=params,
        timeout=20,
    )
    response.raise_for_status()

    payload = None
    try:
        payload = response.json()
    except ValueError:
        payload = response.text

    return _extract_media_url_from_payload(payload)


def get_og_data(url: str) -> dict:
    try:
        clean_url = remove_query_from_url(url)
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/58.0.3029.110 Safari/537.3"
            )
        }
        response = requests.get(clean_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        og_tags = {}
        for tag in soup.find_all("meta"):
            prop = tag.get("property") or tag.get("name")
            if prop and prop.startswith("og:"):
                og_tags[prop] = tag.get("content", "")

        download_link = None
        download_source = None

        try:
            download_link = _fetch_download_link_via_rapidapi(clean_url)
            if download_link:
                download_source = "rapidapi"
        except Exception as rapidapi_exc:
            download_source = "fallback"
            download_link = _extract_download_link(og_tags)
            error_message = str(rapidapi_exc)
        else:
            if not download_link:
                download_link = _extract_download_link(og_tags)
                if download_link:
                    download_source = "fallback"
        result = {
            "title": og_tags.get("og:title", ""),
            "url": clean_url,
            "description": og_tags.get("og:description", ""),
            "thumbnail": og_tags.get("og:image", ""),
            "download_link": download_link,
            "video_available": bool(download_link),
            "embed_code": (
                f'<blockquote class="instagram-media" '
                f'data-instgrm-permalink="{clean_url}" '
                f'data-instgrm-version="14"></blockquote>'
                f'<script async src="//www.instagram.com/embed.js"></script>'
            ),
        }

        if download_source:
            result["download_source"] = download_source
        if download_source == "fallback" and "error_message" in locals():
            result["download_error"] = error_message
        return result
    except Exception as exc:
        return {"message": str(exc)}
