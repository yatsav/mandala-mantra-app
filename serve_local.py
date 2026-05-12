#!/usr/bin/env python3
"""
Serveur local pour tester la PWA Mandala-Mantra sur iPhone via le Wi-Fi.

Usage :
    python3 serve_local.py            # serveur HTTP simple (port 8080)
    python3 serve_local.py --https    # serveur HTTPS auto-signé (port 8443)

Le HTTPS est requis pour que le service worker s'enregistre. iOS Safari
fait une exception sur localhost en HTTP simple, mais depuis un autre
appareil il faudra accepter le certificat auto-signé une fois.
"""
import http.server
import socketserver
import socket
import os
import sys
import subprocess
import ssl
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.chdir(HERE)

PORT_HTTP  = 8080
PORT_HTTPS = 8443

def local_ip():
    """Retourne l'IP locale (192.168.x.x) du Mac sur le réseau Wi-Fi."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Headers indispensables pour PWA
        self.send_header('Service-Worker-Allowed', '/')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

    def log_message(self, fmt, *args):
        # Log moins verbeux
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(),
                                         fmt % args))

def make_self_signed_cert(cert_path, key_path):
    """Crée un certificat auto-signé via openssl si absent."""
    if cert_path.exists() and key_path.exists():
        return
    print("Génération d'un certificat auto-signé (valide 365 jours)…")
    subprocess.run([
        'openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-sha256',
        '-days', '365', '-nodes',
        '-keyout', str(key_path), '-out', str(cert_path),
        '-subj', '/CN=mandala-mantra.local',
        '-addext', f'subjectAltName=DNS:localhost,IP:127.0.0.1,IP:{local_ip()}'
    ], check=True)
    print(f"  → {cert_path}")
    print(f"  → {key_path}")

def main():
    use_https = '--https' in sys.argv
    port = PORT_HTTPS if use_https else PORT_HTTP
    ip = local_ip()
    scheme = 'https' if use_https else 'http'

    with socketserver.TCPServer(('0.0.0.0', port), QuietHandler) as httpd:
        if use_https:
            cert = HERE / '.cert.pem'
            key  = HERE / '.key.pem'
            make_self_signed_cert(cert, key)
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(certfile=str(cert), keyfile=str(key))
            httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)

        print('═' * 60)
        print(' Mandala-Mantra · Serveur local PWA')
        print('═' * 60)
        print(f' Local (ce Mac)     : {scheme}://localhost:{port}/')
        print(f' iPhone (Wi-Fi)     : {scheme}://{ip}:{port}/')
        print('─' * 60)
        if use_https:
            print(' ⚠ Au 1er chargement sur iPhone : Safari affichera un')
            print('   avertissement de certificat → toucher « Détails » → ')
            print('   « visiter ce site web ». Le SW s\'enregistrera ensuite.')
        else:
            print(' Note : le service worker ne s\'enregistre qu\'en HTTPS')
            print('        ou sur localhost. Pour tester sur iPhone, relancer')
            print('        avec --https.')
        print('─' * 60)
        print(' Ctrl+C pour arrêter.')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nArrêt du serveur.')

if __name__ == '__main__':
    main()
