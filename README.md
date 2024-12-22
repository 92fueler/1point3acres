# 1point3acres Crawler

A web crawler designed to collect data from 1point3acres.com, a popular forum for international students and professionals.

## Tech Stack

- Python 3.12+
- uv (Python package manager)
- MongoDB (via Docker)
- BeautifulSoup4
- Requests

## Prerequisites

- Python 3.12+
- Docker
- uv package manager

## Installation

Install dependencies using uv
```bash
uv venv
source .venv/bin/activate
```

Start MongoDB using Docker

```bash
docker run -d
```

Stop MongoDB
```bash
docker stop mongodb
```

View MongoDB logs
```bash
docker logs mongodb
```
