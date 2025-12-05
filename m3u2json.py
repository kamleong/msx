#!/usr/bin/env python3

import sys
#print(sys.argv[0])  ## __file__

filepath = sys.argv[1] if len(sys.argv) > 1 else r"msa.m3u"
#print(filepath)

searchtext = sys.argv[2] if len(sys.argv) > 2 else ""
#print(searchtext)

dictObj = {}
def printM3u(dictObj) :
  print(
    '#EXTINF:-1 tvg-id="" tvg-logo="' + dictObj["tvg-logo"] + '" group-title="",' + dictObj["title"] + "\n" + dictObj["url"]
  )
#
def printMsxJson(dictObj) :
  print(
    ', { "title":"' + dictObj["title"] + '", "image":"' + dictObj["tvg-logo"] + '", "action":"video:' + dictObj["url"]  + '" }'
  )
#
def printTxt(dictObj) :
  print(
    dictObj["url"] + ',' + dictObj["title"].replace(',',' ')  + ',,' + dictObj["tvg-logo"]
  )
#
def printDictObj(dictObj, c) :
  if c=="m3u" :
    printM3u(dictObj)
  elif c=="msx" :
    printMsxJson(dictObj)
  elif c=="txt" :
    printTxt(dictObj)
  else :
    print(dictObj)
  #
  sys.stdout.flush()
#

import subprocess
def curl(url) :
  try:
    rslt = subprocess.run(["curl", "-s", "-L",
      "--connect-timeout", "5", "--max-time", "20",
      "--fail", url
    ], capture_output=True, text=True)
    return rslt.stdout ## .stderr .returncode 
  except Exception as e:
    print(e, file=sys.stderr)
    return ""
  #
#

import re
def parseExtInf(line) :
  dictObj = {"title":"", "url":"", "tvg-logo":""}
  dictObj["title"] = re.sub(r'^.+,', "", line)
  for m in re.findall(r'(\S+)="(.*?)"', line):
    dictObj[m[0].lower()] = m[1]
  #
  #print(dictObj)
  return dictObj
#

def parseM3u(lines, convert=None) :
  for line in lines: 
    line = line.strip()
    if line=="": continue
    if line.startswith("http") :
      if len(curl(line))<1: continue
      dictObj = parseExtInf(lastLine)
      dictObj["url"] = line
      printDictObj(dictObj, convert)
      #break
    elif line.startswith("#EXTINF:-1"):
      lastLine = line
    #
  #
#

import json
def parseMsxJson(jsonString, convert=None) :
  jsonData = json.loads(jsonString)
  for m in jsonData['menu'] :
    print(m['label'])
    d = m['data']
    print(d['headline'])
    for i in d['items'] :
      #print(i)
      dictObj = {
        "title": i['title'],
        "tvg-logo": i['image'],
        "group-title": m['label'],
        "url": i['action'].removeprefix('video:').removeprefix('audio:')
      }
      printDictObj(dictObj, convert)
      break
    #
    break
  #  
#

#with open(filepath) as f1: lines = f1.readlines()
#parseMsxJson(''.join(lines))

# 'https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8'
m3uString = curl('https://iptv-org.github.io/iptv/languages/' + filepath) 
# eng|msa|cmn|zho|nan|yue.m3u
parseM3u(m3uString.split("\n"), "txt")

quit()

with open(filepath) as f1:
  while True: 
    line = f1.readline()
    if not line: break
    line = line.strip()
    if line=="": continue
    if line.startswith("http") :
      dictObj = parseExtInf(lastLine)
      dictObj["url"] = line
      #print(dictObj)
      #break
    #
    lastLine = line
  #
#
