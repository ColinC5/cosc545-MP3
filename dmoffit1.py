import json, re
import requests
from urlextract import URLExtract
import sys, gzip

utid = 'dmoffit1'
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post = '/raw/main/README.md'
postGH = 'blob/master/README.md' # or it could be 'blob/main/README.md'

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'
#r1\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])[[:graph:]])+)\b'

def extractURLs (c):
 res = extU.find_urls (c)
 return res

def extractDOIs (c):
 res = re.findall (DOIpattern, c)
 return res

fo = gzip.open(f"output/{utid}.json.gz", 'w')

def run (tp):
 post0 = post
 with open(f"input/{utid}_{tp}", 'r') as f:
  for line in f:
   line = line.strip ()
   if tp == 'source':
    (npapers,line) = line.split(';');
    post0 = postGH
   print(line)
   url = base[tp] + f"{line}{post0}"
   try:
        r = requests.get (url)
        if r.status_code == 404:
            content = "not found"
        elif r.status_code == 403:
            content = "rate limit exceeded"
        elif r.status_code != 200:
            content = f"Error: {r.status_code}"
        else:
            content = r.text
        #github returns repos that do not exist, need to detect that here
        #github when you give master instead of main, that might cause issues as well
        urls = extractURLs(content)
        dois = extractDOIs(content)
        res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois }
        out = json.dumps(res, ensure_ascii=False)
        fo.write((out+"\n").encode())
   except requests.exceptions.RequestException as e:
        content = f"Error: {str(e)}"
        # If the request failed, no valid content, but still log it
        urls = []
        dois = []
        res = {'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois}
        out = json.dumps(res, ensure_ascii=False)
        fo.write((out + "\n").encode())
    
run('model')
run('data')
run('source')
