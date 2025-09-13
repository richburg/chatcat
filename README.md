# chatcat
Asynchronous and concurrent TCP chatting server using raw text for communication. There is no versioning because of its rolling-release nature.

## Configuration
Edit `server/config.py`. The variables are highly self-documented with type annotations.

## Quick Start
Get up and running in seconds:
```bash
python3 -m server
```

## Production Deployment
```bash
docker build -t chat-server .
docker run -p 5000:5000 chat-server
```
