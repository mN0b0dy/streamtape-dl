# streamtape-dl
 Download contents from [Streamtape](https://streamtape.com) by utilizing the API.

 ### Requirements
 ```
 pip3 install -r requirements.txt
 ```

 ### Development
 Enable the `DEBUG` flags in all files for full verbose debug:
 ```
 helpers.py -- DEBUG = 1
 run.py -- DEBUG = 1
 ```
 [API documentation](https://streamtape.com/api).

 ### Usage
 1. Create an account in streamtape.com and get these `API Username`, `API Password` credentials from the account panel.

 2. Paste those two things in `example.env` and rename it to `.env` afterwards. Do not add inverted comma or quotes.
 
 ```
 python3 run.py <url> [url0,...,urlN]
 ```
 
 ### Features
    - Supports multiple instances.
    - Download progress bar.
    - Verbose output.
