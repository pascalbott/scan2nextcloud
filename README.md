# Scan2Nextcloud

A Docker-based SMB scan server for network printers that automatically
uploads scanned PDF files to a Nextcloud instance via WebDAV.

Designed for Raspberry Pi, homelab environments, and small business
deployments.

------------------------------------------------------------------------

## Docker Hub

Pull the latest image:

    docker pull pascalbott/scan2nextcloud:latest

Docker Hub repository:

https://hub.docker.com/r/pascalbott/scan2nextcloud

------------------------------------------------------------------------

## Features

-   SMB share with username and password authentication
-   Automatic upload to Nextcloud via WebDAV
-   File stability check for large PDF scans
-   Retry logic for temporary network failures
-   Polling observer for Raspberry Pi compatibility
-   Automatic timestamping to prevent duplicate filenames
-   Archive of successfully uploaded files
-   Production-ready structured logging

------------------------------------------------------------------------

## Quick Start (Recommended)

Clone the repository:

    git clone https://github.com/pascalbott/scan2nextcloud.git
    cd scan2nextcloud

Create your environment configuration:

    cp .env.example .env

Edit the `.env` file and configure your values.

Start the container:

    docker compose up -d

View logs:

    docker logs -f scan2nextcloud

------------------------------------------------------------------------

## Example docker-compose.yml

``` yaml
version: "3.8"

services:
  scan2nextcloud:
    image: pascalbott/scan2nextcloud:latest
    container_name: scan2nextcloud
    ports:
      - "445:445"
    volumes:
      - ./data/scan:/scan
      - ./data/uploaded:/uploaded
    env_file:
      - .env
    restart: unless-stopped
```

------------------------------------------------------------------------

## Environment Configuration

This project uses environment variables via a `.env` file.

Example `.env.example`:

    SMB_USER=scanner
    SMB_PASS=ChangeMeSecurePassword

    NEXTCLOUD_URL=https://cloud.example.com
    NEXTCLOUD_USER=nextcloud_user
    NEXTCLOUD_PASS=NEXTCLOUD_APP_PASSWORD
    NEXTCLOUD_FOLDER=Documents/Scans

Important:

-   Do NOT commit your `.env` file.
-   Always use a Nextcloud App Password.
-   The username in the WebDAV path must match `NEXTCLOUD_USER`.

------------------------------------------------------------------------

## Run Without docker-compose

You can also run the container directly:

    docker run -d   -p 445:445   -v $(pwd)/data/scan:/scan   -v $(pwd)/data/uploaded:/uploaded   --env-file .env   pascalbott/scan2nextcloud:latest

------------------------------------------------------------------------

## Nextcloud Configuration

WebDAV endpoint format:

    https://DOMAIN/remote.php/dav/files/USERNAME/FOLDER/PATH

Example:

    https://cloud.example.com/remote.php/dav/files/nextcloud_user/Documents/Scans

------------------------------------------------------------------------

## Printer Configuration

Server:

    192.168.0.150

Share:

    scan

Username:

    scanner

Password:

    YourSMBPassword

Network path:

    \\192.168.0.150\scan

------------------------------------------------------------------------

## How It Works

1.  The printer scans a PDF into the SMB share.
2.  The system waits until the file size stabilizes.
3.  The file is uploaded to Nextcloud via WebDAV.
4.  The file receives a timestamp to prevent name conflicts.
5.  The file is moved to the local archive directory.

Example filename:

    20260220_153012_scan.pdf

------------------------------------------------------------------------

## Security Recommendations

For production deployments:

-   Use a dedicated Nextcloud user
-   Use Nextcloud App Passwords
-   Restrict port 445 to the local network only
-   Configure a firewall
-   Keep Docker images and system packages updated
-   Consider Docker secrets instead of environment variables

------------------------------------------------------------------------

## Architecture

Printer → SMB → Docker Container → WebDAV → Nextcloud

------------------------------------------------------------------------

## License

MIT License recommended for open source distribution.