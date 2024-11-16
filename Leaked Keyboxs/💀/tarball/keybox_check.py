# Telegram @cleverestech
import requests
import os
import xml.etree.ElementTree as ET
from cryptography import x509
import argparse
from colorama import Fore, Style, init
from typing import Optional, List
import logging
import sys

# Initialize colorama
init(autoreset=True)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# ANSI escape codes for bold text
BOLD = Style.BRIGHT

# Constants
CRL_URL = 'https://android.googleapis.com/attestation/status'
TIMEOUT = 10

# Setup argument parser
parser = argparse.ArgumentParser(description='Check keybox files for certificate validity against CRL (only processes .xml files).')
parser.add_argument('path', type=str, nargs='?', default=os.getcwd(),
                    help='Path to the directory containing keybox files (default: current directory)')
args = parser.parse_args()

def fetch_crl(url: str, timeout: int = TIMEOUT) -> Optional[dict]:
    """Fetch Certificate Revocation List (CRL) with cache and cookies disabled."""
    try:
        session = requests.Session()
        session.cookies.clear()
        headers = {
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
        response = session.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch CRL: {e}")
        return None

crl = fetch_crl(CRL_URL)
if crl is None:
    logging.critical("Unable to proceed without a valid CRL.")
    sys.exit(1)

def parse_cert(cert: str) -> Optional[str]:
    """Parse a certificate and return its serial number."""
    try:
        cert = "\n".join(line.strip() for line in cert.strip().split("\n"))
        parsed = x509.load_pem_x509_certificate(cert.encode())
        return f'{parsed.serial_number:x}'
    except ValueError:
        logging.error("Error parsing certificate.")
        return None

def extract_certs(file_path: str) -> List[str]:
    """Extract certificates from Keybox files (only .xml files)."""
    if not file_path.lower().endswith('.xml'):
        return []

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        return [elem.text for elem in root.iter() if elem.tag == 'Certificate']
    except ET.ParseError:
        logging.warning(f"{BOLD}{os.path.basename(file_path)} could not be parsed as XML.")
        return []

def main():
    total_keyboxes = revoked_keyboxes = valid_keyboxes = invalid_keyboxes = invalid_files = 0

    directory = args.path
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isdir(file_path):
            continue

        if not filename.lower().endswith('.xml'):
            invalid_files += 1
            continue

        total_keyboxes += 1
        certs = extract_certs(file_path)

        if len(certs) < 4:
            logging.info(f"{Fore.YELLOW}{BOLD}{filename} doesn't contain enough certificate data!")
            invalid_keyboxes += 1
            continue

        ec_cert_sn = parse_cert(certs[0])
        rsa_cert_sn = parse_cert(certs[3])

        if not ec_cert_sn or not rsa_cert_sn:
            logging.warning(f"{filename} - Error parsing certificate data.")
            invalid_keyboxes += 1
            continue

        if any(sn in crl["entries"] for sn in (ec_cert_sn, rsa_cert_sn)):
            logging.info(f"{Fore.RED}{BOLD}{filename} Key has been revoked.")
            logging.info(f"   EC Cert Serial Number: {ec_cert_sn}\n   RSA Cert Serial Number: {rsa_cert_sn}")
            revoked_keyboxes += 1
        else:
            logging.info(f"{Fore.GREEN}{BOLD}{filename} is valid.")
            logging.info(f"   EC Cert Serial Number: {ec_cert_sn}\n   RSA Cert Serial Number: {rsa_cert_sn}")
            valid_keyboxes += 1

    logging.info(f'\n{Fore.CYAN}{BOLD}Summary:')
    logging.info(f'  Total XML files examined: {total_keyboxes}')
    logging.info(f'  Valid Certificates: {valid_keyboxes}')
    logging.info(f'  Revoked Certificates: {revoked_keyboxes}')
    logging.info(f'  Invalid Keyboxes: {invalid_keyboxes}')
    logging.info(f'  Non-XML Files: {invalid_files}')

if __name__ == "__main__":
    main()
