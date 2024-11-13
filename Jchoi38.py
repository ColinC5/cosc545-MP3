import json, re
import requests
from urlextract import URLExtract
import sys, gzip


utid = 'jchoi38'
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post = '/raw/main/README.md'
postGH = '/blob/master/README.md' # or it could be 'blob/main/README.md
postGH_main = '/blob/main/README.md'

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'
BIBpattern = r'@(?:article|book|inproceedings|misc|techreport)\{[^}]+\}' # From ChatGPT
# r1\b(10[.][0-9]{4,}(?:[.][0-39]+)*/(?:(?!["&\'<>])[[:graph:]])+)\b'

def extractURLs (c):
 res = extU.find_urls (c)
 return res

def extractDOIs (c):
 res = re.findall (DOIpattern, c)
 return res

def extractBIBs (c):
 res = re.findall (BIBpattern, c)
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
   url = base[tp] + f"{line}{post0}"
   print(url)

   r = requests.get (url)
   #github returns repos that do not exist, need to detect that here
   if r.status_code == 404:
    #github when you give master instead of main, that might cause issues as well
    if tp != 'source': continue
    else:
      url_main = base[tp] + f"{line}{postGH_main}"
      r = requests.get(url_main)
      print(url_main)
      if r.status_code == 404: continue
   content = r.text

   urls = extractURLs(content)
   dois = extractDOIs(content)
   bibs = extractBIBs(content)
   res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois, 'bibs': bibs }
   out = json.dumps(res, ensure_ascii=False)
   fo.write((out+"\n").encode())


run('model')
run('data')
run('source')

fo.close()