FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y samba samba-common-bin && \
    pip install watchdog requests && \
    apt-get clean

RUN mkdir -p /scan /uploaded

COPY smb.conf /etc/samba/smb.conf
COPY upload.py /upload.py
COPY start.sh /start.sh

RUN chmod +x /start.sh

EXPOSE 445

CMD ["/start.sh"]