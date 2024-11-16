# Telegram @cleverestech
import requests
import os
import xml.etree.ElementTree as ET
from cryptography import x509
import argparse
from colorama import Fore, Style, init
from typing import Optional, List
import logging

# Initialize colorama
init(autoreset=True)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# ANSI escape codes for bold text
BOLD = Style.BRIGHT

'''
Usage: keybox_check.py [path]

Checks only .xml keybox files in the specified directory for EC and RSA certificates against the official CRL. Ensures no caching and disables cookies when fetching CRL
'''

# Setup argument parser
parser = argparse.ArgumentParser(description='Check keybox files for certificate validity against CRL (only processes .xml files).')
parser.add_argument('path', type=str, nargs='?', default=os.getcwd(),
                    help='Path to the directory containing keybox files (default: current directory)')
args = parser.parse_args()

# Function to fetch the Certificate Revocation List (CRL) with bypassed cache and cookies
def fetch_crl(url: str) -> Optional[dict]:
    try:
        # Ensure requests do not store cookies or use cached data
        session = requests.Session()
        session.cookies.clear()  # Ensure no cookies are sent
        # Apply headers to prevent caching
        headers = {
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'            
        }
        response = session.get(url, headers=headers, timeout=10)        
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch CRL: {e}")
        return None

# Fetch the CRL data
crl = fetch_crl('https://android.googleapis.com/attestation/status')
if crl is None:
    logging.critical("Unable to proceed without a valid CRL.")
    exit(1)

# Function to parse certificate serial numbers from PEM format
def parse_cert(cert: str) -> Optional[str]:
    try:
        cert = "\n".join(line.strip() for line in cert.strip().split("\n"))
        parsed = x509.load_pem_x509_certificate(cert.encode())
        return f'{parsed.serial_number:x}'
    except ValueError:
        logging.error("Error parsing certificate.")
        return None

# Function to extract certificates from Keybox (only processes XML files now additionally)
def extract_certs(file_path: str) -> List[str]:
    if not file_path.lower().endswith('.xml'):
        return [] # Skip file if it's not XML

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        return [elem.text for elem in root.iter() if elem.tag == 'Certificate']
    except ET.ParseError:
        logging.warning(f"{BOLD}{os.path.basename(file_path)} could not be parsed as XML.")
        return []

# Initialize counters
total_keyboxes = 0
revoked_keyboxes =  0
valid_keyboxes = 0
invalid_keyboxes = 0
invalid_files = 0

# Directory argument
directory = args.path

# Iterate over all files in the directory
for filename in os.listdir(directory):
    file_path = os.path.join(directory, filename)    
    if os.path.isdir(file_path):  
        continue     

    if not filename.endswith(".xml"):     
        invalid_files = invalid_files + 1        
        continue
      
    total_keyboxes = total_keyboxes + 1          
    certs = extract_certs(file_path)

    if len(certs) < 4:
        logging.info(f"{Fore.YELLOW}{BOLD}{filename}  don't coontains enough cert data! ")
        invalid_keyboxes = invalid_keyboxes + 1
        continue

    # Process extracted certificates 
    ec_cert_sn = parse_cert(certs[0])
    rsa_cert_sn  = parse_cert(certs[3])

    if not ec_cert_sn or not rsa_cert_sn:
         logging.warning(f"{filename}, A significant error raised since its not possible parse certificate data from certificate source")                
         invalid_keyboxes = invalid_keyboxes + 1
         continue   

    # Verify certificates against CRL data fetch that resulted from hitting the network endpoint endpoint provided  
    if any(sn in crl["entries"] for sn in (ec_cert_sn, rsa_cert_sn)):            
        print(f'{Fore.RED}{BOLD}{filename} Key has been Revoked')

        print(f'   EC Cert Serial Numer: {ec_cert_sn} Certificate \n  Rsa  SN : {rsa_cert_sn}')            
        revoked_keyboxes += 1
             
    else:                            
        print(f'{Fore.GREEN}{BOLD}{filename} is on validation phase, thus all ok!')                 
        print(f'   EC Cert Serial Num:  {ec_cert_sn}\n    RSA Cert  SN :  {rsa_cert_sn}')
        valid_keyboxes = valid_keyboxes + 1
                     
# Summary Results      
print (f'\n{Fore.CYAN}{BOLD}Summary:')
print (f'  Total XML files on disk to examine {total_keyboxes}')
print(f' Cert Key Status - OK :: {valid_keyboxes}')    
print (f' Detected amount revocation attempts: -> Total counts {revoked_keyboxes}') 
print(f' Detected errors/keys that could no be parsed -> counts are {invalid_keyboxes}')
print(f' Total errors of failed I/O read/right when extracting info {invalid_files}') 