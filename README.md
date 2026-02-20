# Scan2Nextcloud

A Docker-based SMB scan server for network printers that automatically
uploads scanned PDF files to a Nextcloud instance via WebDAV.

Designed for Raspberry Pi, homelab environments, and small business
deployments.

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

## Project Structure

    scan2nextcloud/
    ├── Dockerfile
    ├── docker-compose.yml
    ├── start.sh
    ├── upload.py
    └── smb.conf

------------------------------------------------------------------------

## Example docker-compose.yml

``` yaml
version: "3.8"

services:
  scan2nextcloud:
    build: .
    container_name: scan2nextcloud
    ports:
      - "445:445"
    volumes:
      - ./data/scan:/scan
      - ./data/uploaded:/uploaded
    environment:
      SMB_USER: "scanner"
      SMB_PASS: "ChangeMeSecurePassword"
      NEXTCLOUD_URL: "https://cloud.example.com"
      NEXTCLOUD_USER: "nextcloud_user"
      NEXTCLOUD_PASS: "NEXTCLOUD_APP_PASSWORD"
      NEXTCLOUD_FOLDER: "Documents/Scans"
      PYTHONUNBUFFERED: "1"
    restart: unless-stopped
```

------------------------------------------------------------------------

## Nextcloud Configuration

WebDAV endpoint format:

    https://DOMAIN/remote.php/dav/files/USERNAME/FOLDER/PATH

Example:

    https://cloud.example.com/remote.php/dav/files/nextcloud_user/Documents/Scans

Important: The username in the WebDAV path must match the value of
NEXTCLOUD_USER.

Always use a Nextcloud App Password instead of your main login password.

------------------------------------------------------------------------

## Printer Configuration

Server:

    192.168.0.150

Share:

    scan

Username:

    scanner

Password:

    ChangeMeSecurePassword

Network path:

    \\192.168.0.150\scan

------------------------------------------------------------------------

## Start the Container

Build and run:

    docker compose up -d --build

View logs:

    docker logs -f scan2nextcloud

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

Intended for private and internal business use.