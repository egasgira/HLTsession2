#! /usr/bin/python3

import sys
import re
from os import listdir
import nltk
#from nltk.corpus import stopwords
#nltk.download('stopwords')
from xml.dom.minidom import parse
from nltk.tokenize import word_tokenize


   
## --------- tokenize sentence ----------- 
## -- Tokenize sentence, returning tokens and span offsets

def tokenize(txt):
    offset = 0
    tks = []
    ## word_tokenize splits words, taking into account punctuations, numbers, etc.
    for t in word_tokenize(txt):
        ## keep track of the position where each token should appear, and
        ## store that information with the token
        offset = txt.find(t, offset)
        tks.append((t, offset, offset+len(t)-1))
        offset += len(t)

    ## tks is a list of triples (word,start,end)
    return tks


## --------- get tag ----------- 
##  Find out whether given token is marked as part of an entity in the XML

def get_tag(token, spans) :
   (form,start,end) = token
   for (spanS,spanE,spanT) in spans :
      if start==spanS and end<=spanE : return "B-"+spanT
      elif start>=spanS and end<=spanE : return "I-"+spanT

   return "O"
 
## --------- Feature extractor ----------- 
## -- Extract features for each token in given sentence

def extract_features(tokens) :

   #stopWords = set(stopwords.words('english'))
   # for each token, generate list of features and add it to the result
   result = []
   for k in range(0,len(tokens)):
      tokenFeatures = [];
      t = tokens[k][0]

      tokenFeatures.append("form="+t)
      tokenFeatures.append("suf3="+t[-3:])
      tokenFeatures.append("formLower=" + t.lower())
      tokenFeatures.append("speialChars=" + str(bool(re.search("(?=.[a-zA-Z])(?=.[-()0-9])", t))))
      tokenFeatures.append("firstCap=" + str(bool(t[0].isupper() and t[1:].islower())))
      tokenFeatures.append("allCap-1=" + str(bool(t[:-2].isupper())))
      #tokenFeatures.append("post3" +t[:3])
      tokenFeatures.append("post4" + t[:4])
      #tokenFeatures.append("suf1="+t[-1:])
      tokenFeatures.append("len="+str(len(t)))
      #tokenFeatures.append("nUpper=" + str(sum([c.isdigit() for c in t])))
      #tokenFeatures.append("stop=" + str(bool(t.lower() in stopWords)))


#      if k>2 :
##         t3Prev =tokens[k-3][0]
#         tokenFeatures.append("form3PrevLower=" + t3Prev.lower())
#         tokenFeatures.append("form3Prev=" + t3Prev)
#         tokenFeatures.append("suf33Prev=" + t3Prev[-3:])#

      if k>1 :
         t2Prev =tokens[k-2][0]
         tokenFeatures.append("form2PrevLower=" + t2Prev.lower())
         tokenFeatures.append("form2Prev=" + t2Prev)
         tokenFeatures.append("suf32Prev=" + t2Prev[-3:])

      if k>0 :
         tPrev = tokens[k-1][0]
         tokenFeatures.append("formPrevLower=" + tPrev.lower())
         tokenFeatures.append("formPrev="+tPrev)
         tokenFeatures.append("suf3Prev="+tPrev[-3:])
         #tokenFeatures.append("allCap-1Prev=" + str(bool(tPrev[:-2].isupper())))
         #tokenFeatures.append("firstCapPrev=" + str(bool(tPrev[0].isupper() and tPrev[1:].islower())))
         #tokenFeatures.append("post3Prev" + tPrev[:3])
      else :
         tokenFeatures.append("BoS")

      if k<len(tokens)-1 :
         tNext = tokens[k+1][0]
         tokenFeatures.append("formNextLower="+ tNext.lower())
         tokenFeatures.append("formNext="+tNext)
         tokenFeatures.append("suf3Next="+tNext[-3:])
         tokenFeatures.append("allCap-1Next=" + str(bool(tNext[:-2].isupper())))

         #tokenFeatures.append("firstCapNext=" + str(bool(tNext[0].isupper() and tNext[1:].islower())))
         #tokenFeatures.append("post3Next" + tNext[:3])
         #tokenFeatures.append("lenNext=" + str(len(tNext)))
      else:
         tokenFeatures.append("EoS")
    
      result.append(tokenFeatures)
    
   return result


## --------- MAIN PROGRAM ----------- 
## --
## -- Usage:  baseline-NER.py target-dir
## --
## -- Extracts Drug NE from all XML files in target-dir, and writes
## -- them in the output format requested by the evalution programs.
## --


# directory with files to process
datadir = sys.argv[1]

# process each file in directory
for f in listdir(datadir) :
   
   # parse XML file, obtaining a DOM tree
   tree = parse(datadir+"/"+f)
   
   # process each sentence in the file
   sentences = tree.getElementsByTagName("sentence")
   for s in sentences :
      sid = s.attributes["id"].value   # get sentence id
      spans = []
      stext = s.attributes["text"].value   # get sentence text
      entities = s.getElementsByTagName("entity")
      for e in entities :
         # for discontinuous entities, we only get the first span
         # (will not work, but there are few of them)
         (start,end) = e.attributes["charOffset"].value.split(";")[0].split("-")
         typ =  e.attributes["type"].value
         spans.append((int(start),int(end),typ))
         

      # convert the sentence to a list of tokens
      tokens = tokenize(stext)
      # extract sentence features
      features = extract_features(tokens)

      # print features in format expected by crfsuite trainer
      for i in range (0,len(tokens)) :
         # see if the token is part of an entity
         tag = get_tag(tokens[i], spans) 
         print (sid, tokens[i][0], tokens[i][1], tokens[i][2], tag, "\t".join(features[i]), sep='\t')

      # blank line to separate sentences
      print()
