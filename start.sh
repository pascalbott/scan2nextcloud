#!/bin/bash
set -e

# Linux User erstellen falls nicht existiert
id -u "$SMB_USER" &>/dev/null || useradd -M -s /sbin/nologin "$SMB_USER"

# SMB Passwort non-interaktiv setzen
(echo "$SMB_PASS"; echo "$SMB_PASS") | smbpasswd -s -a "$SMB_USER"

# Rechte setzen
chown -R "$SMB_USER":"$SMB_USER" /scan
chmod -R 770 /scan

# Samba im Hintergrund starten
smbd -F &

# Python Upload Script starten
python /upload.py