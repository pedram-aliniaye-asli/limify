# Installation

## Requirements

- Python 3.10+
- Redis

---

## Install Limify

```
pip install limifyrate
```

---

## Install with FastAPI adapter

```
pip install "limifyrate[fastapi]"
```

---

## Development Installation

```
git clone https://github.com/pedram-aliniaye-asli/limify.git
cd limify
pip install -e ".[dev]"
```

---

## Redis Setup

Example Redis instance:

```
redis-server
```

Or using Docker:

```
docker run -p 6379:6379 redis
```
