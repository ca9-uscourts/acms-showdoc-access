import requests
import re
import tempfile
import gzip
import urllib.parse
import xml.etree.ElementTree as ET
from requests.cookies import RequestsCookieJar

# UPDATE TO YOUR PACER CREDENTIALS
pacer_login_id = 'PACER_USER'
pacer_password = 'PACER_PASSWORD'
pacer_client_code = ''  # set to code or leave blank
user_ip_address = ''  # set to your public IP address

# UPDATE TO TARGET CASE
docket_sheet_url = 'https://ca9-showdoc.azurewebsites.us/22-54'

login_url = 'https://pacer.login.uscourts.gov/services/cso-auth'
# Create XML payload for authentication
post_fields = f'''<?xml version="1.0" encoding="UTF-8"?>
                    <CsoAuth>
                        <loginId>{pacer_login_id}</loginId>
                        <password>{pacer_password}</password>
                        <clientCode></clientCode>
                        <redactFlag>1</redactFlag>
                    </CsoAuth>'''

# Create a session to maintain cookies
session = requests.Session()
cookies = RequestsCookieJar()
session.cookies = cookies

# Configure the session
session.verify = False  # Equivalent to CURLOPT_SSL_VERIFYPEER
session.headers.update({
    'Content-Type': 'application/xml',
    'Accept': 'application/xml'
})

# Get PACER nextGenCSO token
try:
    response = session.post(login_url, data=post_fields)
    print(f"Curl session 1 worked.\n{response.text}\n")
    
    # Extract nextGenCSO token
    next_gen_cso = None
    if '<nextGenCSO>' in response.text:
        result_parts = response.text.split('<nextGenCSO>')
        if len(result_parts) >= 2:
            result_parts_2 = result_parts[1].split('</nextGenCSO>')
            if len(result_parts_2) >= 2:
                next_gen_cso = result_parts_2[0]
                print(f"nextGenCSO is: {next_gen_cso}\n")
except Exception as e:
    print(f"Curl session failed.\n{str(e)}\n")
    exit()

# Get ACMS docket sheet
if next_gen_cso:
    try:
        session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'X-NEXT-GEN-CSO': next_gen_cso,
            'X-PACER-CLIENT-CODE': pacer_client_code,
            'X-USER-IP-ADDRESS': user_ip_address
        })
        
        response = session.post(docket_sheet_url)
        
        # Split response parts
        result_parts = response.text.split("\r\n")
        print(f"Docket result_parts: {result_parts}\n\n\n")
        
        # Handle gzip decoding
        java_script_screen = result_parts[-1]
        try:
            # Try to decompress if it's gzipped
            inflated_screen = gzip.decompress(java_script_screen.encode()).decode()
        except:
            # If decompression fails, use the original
            inflated_screen = java_script_screen
            
        print(f"javascriptScreen: {inflated_screen}\n\n")
        
        # Perform a POST to get to next page
        matches = re.findall(r'<input type="hidden" name="([A-Za-z]*)" value="([^"]*)"/>', inflated_screen)
        print(f"matches are: {matches}\n")
        
        if matches:
            post_fields = f"{matches[0][0]}={urllib.parse.quote(matches[0][1])}&{matches[1][0]}={urllib.parse.quote(matches[1][1])}"
            print(f"postFields are: {post_fields}\n\n\n")
            
            # POST with SAML token
            session.headers.update({
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-NEXT-GEN-CSO': next_gen_cso,
                'X-PACER-CLIENT-CODE': pacer_client_code,
                'X-USER-IP-ADDRESS': user_ip_address
            })
            
            saml_url = 'https://ca9-showdoc.azurewebsites.us/Saml2/Acs'
            response = session.post(saml_url, data=post_fields)
            print(f"POST action worked : \n{response.text}\n")
    except Exception as e:
        print(f"Curl failed.\n{str(e)}\n")