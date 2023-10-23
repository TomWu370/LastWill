import ipfsApi
from src import databaseUtil, gmailAPI

def getFileIPFS(url):
    api = ipfsApi.Client(host='https://ipfs.infura.io', port=5001)
    file = api.get(url)

files = databaseUtil.getFileURLs(address, remail)
for file in files:
    gmailAPI.send("name", "this is your file", file=file)
