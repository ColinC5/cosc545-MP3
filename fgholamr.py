import json, re
import requests
from urlextract import URLExtract
import sys, gzip


utid = 'fgholamr'
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post = '/raw/main/README.md'
postGH = '/blob/master/README.md' # or it could be 'blob/main/README.md'
postGHMain = '/blob/main/README.md' #changed to raw in order to avoid massive html inputs in content

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'

Bibpattern = r'@(\w+)\s*{([^@]*)}'


def extractURLs (c):
 res = extU.find_urls (c)
 return res

def extractDOIs (c):
 res = re.findall (DOIpattern, c)
 return res

def extractBibs(c): # returning bibpattern
 res = re.findall(Bibpattern, c)
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
   print(url) #checking for errors in url
   r = requests.get (url)
   print(post0)
   if r.status_code != 200:  # included 200 to get a larger number of errors
   #if r.status_code != 404:
      print(f"{r.status_code}, Error at {url} try main") ## Id url error, try switching to Main
      post0=postGHMain
      #print(f"updated readme to main", post0) 
      
      
      
      url = base[tp] + f"{line}{post0}"
      print(f"updated master to main new url is: {url}") #checking correct url implementation
      r = requests.get (url) # reinit request
      if r.status_code != 200: # Empty repo move to next repo
         print("Empty Master and Main readme")
         continue
      
      
      
   content = r.text;
   #github returns repos that do not exist, need to detect that here
   #github when you give master instead of main, that might cause issues as well
   urls = extractURLs(content)
   dois = extractDOIs(content)
   bibs = extractBibs(content) 
   res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois ,'bib': bibs}
   out = json.dumps(res, ensure_ascii=False)
   fo.write((out+"\n").encode())

run('model')
run('data')
run('source')
