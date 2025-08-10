# kyctester

This repository provides a simple FastAPI service that extracts data from the MRZ (Machine Readable Zone) of an uploaded document image.

## Running with Docker

Build the image:

```bash
docker build -t kyctester .
```

Run the container:

```bash
docker run -p 8000:8000 kyctester
```

The service exposes a `/verify` endpoint that accepts an uploaded image of a document and returns gender and age information inferred from the MRZ.

