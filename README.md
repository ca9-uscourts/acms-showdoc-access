# ACMS ShowDoc Access

Example python code to obtain and use PACER auth tokens to access CA9 ACMS ShowDoc pages.

### Important Notes
* This code only demonstrates how to access the ACMS ShowDoc page. Additional code will be required to download other docket assets.
* Requires an active PACER account with access to the CA9 ACMS system
* This code does not handle JavaScript rendering of curl calls. The ACMS ShowDoc pages require JavaScript execution to display content properly, you will need to modify the code to use a headless browser solution like Selenium or Playwright instead of simple HTTP requests.

### References
PACER Auth API : https://pacer.uscourts.gov/help/pacer/pacer-authentication-api-user-guide
