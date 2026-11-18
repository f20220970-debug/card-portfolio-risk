"""Fetch the source panel into data/.   python src/get_data.py   (~5 MB)

UCI "Default of Credit Card Clients" (Yeh & Lien, 2009): 30,000 Taiwanese card
accounts, six billing months (April-September 2005), labelled with whether the
account defaulted on the following month's payment.  Public research dataset,
no personal identifiers.
"""
import urllib.request
from pathlib import Path

URL = ("https://raw.githubusercontent.com/MatteoM95/"
       "Default-of-Credit-Card-Clients-Dataset-Analisys/main/dataset/"
       "default%20of%20credit%20card%20clients.xls")
OUT = Path(__file__).resolve().parents[1] / "data" / "uci_default.xls"

if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        print(f"already present: {OUT}")
    else:
        print("downloading ~5 MB")
        urllib.request.urlretrieve(URL, OUT)
        print("saved", OUT)
