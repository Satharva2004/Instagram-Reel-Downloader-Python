# Reels Media Fetcher API

## Overview
Fast Flask microservice that turns Instagram or OG-friendly links into clean metadata and ready-to-use download hints made for ps project as i dont have instagram and other softwares show ads.

## Features
- **Simple endpoint**: `POST /api/extract` accepts `{ "url": "https://example.com" }` and responds with OG details.
- **Download link**: Uses RapidAPI for downloading reels or content rate limit is (40 per month) free tier.
- **Embed ready**: Generates Instagram embed code alongside titles, descriptions, and thumbnails.

## Quick Start
1. Create a virtual environment and install dependencies:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
2. Set environment variables in `.env` (copy `.env.example` if available):
```bash
RAPIDAPI_KEY=your_key_here
RAPIDAPI_HOST=instagram-downloader-download-instagram-stories-videos4.p.rapidapi.com
```
3. Launch the server:
```bash
python app.py
```

## Request Example
```bash
curl -X POST http://localhost:5000/api/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.instagram.com/p/xyz/"}'
```

## Response Snapshot
```json
{
  "data": {
    "title": "Sample Reel",
    "thumbnail": "https://...jpg",
    "download_link": "https://...mp4",
    "video_available": true
  }
}
```
