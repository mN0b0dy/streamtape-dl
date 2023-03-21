import pycurl
import requests
from tqdm import tqdm

def pycurl_download(url, outfile, total_size):
    # create a progress bar and update it manually
    with tqdm(total=total_size, unit='iB', unit_scale=True) as pbar:
        # store dotal dl's in an array (arrays work by reference)
        total_dl_d = [0]
        def status(download_t, download_d, upload_t, upload_d, total=total_dl_d):
            # increment the progress bar
            pbar.update(download_d - total[0])
            # update the total dl'd amount
            total[0] = download_d

        # download file using pycurl
        with open(outfile, 'wb') as f:
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(c.WRITEDATA, f)
            # follow redirects:
            c.setopt(c.FOLLOWLOCATION, True)
            # custom progress bar
            c.setopt(c.NOPROGRESS, False)
            c.setopt(c.XFERINFOFUNCTION, status)
            c.perform()
            c.close()

def requests_download(url, outfile, total_size):
    session = requests.Session()
    r = requests.get(url)
    open(outfile, 'wb').write(r.content)

