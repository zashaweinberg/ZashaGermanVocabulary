
# under WSL2
#  cd /c/zasha/code/ZashaGermanVocabulary
#  python3 ProcessDeutschWoerter.py --url https://zashaweinberg.github.io/ZashaGermanVocabulary/deutsch-woerter.html /c/zasha/work/zasha/Deutsche-Klasse/Deutsche-Woerter.docx deutsch-woerter.tsv deutsch-woerter.html

# put deutsch-woerter.html somewhere on the web.
# for new GitHub repository, just commit and push respository
# CAREFUL about pushing changes to deutsch-woerter.html if I'm just playing and don't want to update Anki

# in Windows Anki App (make sure to synchronize the Android App, then the Windows App): Select 'import' (under 'File' menu).  Select the file 'deutsch-woerter.tsv'.  'Fields separated by: Tab' should be selected.  'Update existing notes when first field matches' should be selected.  'Allow HTML in fields' should be checked.  Following should be in effect: 'Field 1 of file is: mapped to Front' and 'Field 2 of file is: mapped to Back'.  Then click 'Import'.
# delete cards that get duplicated because Anki apparently doesn't notice they're the same.  see Google Doc "Neue-deutsche-Woerter", search for "cemile".
# Then click 'Sync'
# In AnkiDroid, While looking at "Stapeln", drag down to synchronize.

# OLD STUFF
# If it's under apache, you might need to set the encoding to UTF-8 in the HTTP headers like so, in the .htaccess file for the relevant directory:
#<Files "deutsch-woerter.html">
#AddCharset UTF-8 .html
#</Files>
# BTW: this doesn't work on Chrome on Windows (it seems to display the file as if it were ASCII), but it does work on the Samsung browser on my phone, so good enough for me.
# scp /c/zasha/temp-away-from-work/deutsch-woerter.html ahvaz:public_html/

import sys
import csv
import string
import argparse
import re
import xml.etree.ElementTree as ElementTree
import zipfile
import itertools
import random
import os.path
import shutil

debugLevel=False # debug going up & down indentation levels
debugCardData=True # print the data for the cards as we parse it

def textToHtml (text):
    html=text
    html=re.sub(r'<','&lt;',html)
    html=re.sub(r'>','&gt;',html)
    html=re.sub(r'\n','<br/>',html)
    return html

def NormalizeSymbolsEspeciallyQuotes (s):
    # substitute weird Unicode characters with normal ones, mainly weird quote characters that Word uses
    for weirdReplace in [ [u'\u201c','"'], [u'\u201d','"'], [u'\u201e','"'], ['\xa0',' '] ]:
        x,y=weirdReplace
        s=s.replace(x,y)
    s=re.sub(r' +$','',s) # get rid of trailing whitespace, although it actually doesn't really matter
    return s

def GetStringUpToFirstQuote (s):
    s=NormalizeSymbolsEspeciallyQuotes(s)
    quoteSplitList=s.split('"')
    return quoteSplitList[0]

def SelectWord(wordList):
    word=wordList[random.randrange(0,len(wordList))]
    return word

# return: True iff either (1) there was an example sentence, or (2) the user said it's okay that there wasn't any example
def HandleBulletText(cardList,fillInBlankCardList,sentenceSeen,definitionInfoStack,currHtml,url,bulletId):

    findNOEXAMPLE=currHtml.find('NOEXAMPLE')
    if findNOEXAMPLE>=0: # user's decided there's no example, so there's nothing for us to do here
        return True # there's no example sentence, but the user said it's okay

    currHtml=NormalizeSymbolsEspeciallyQuotes(currHtml)
    
    quoteSplitList=currHtml.split("\"")
    definitionHtml=None
    expectExample=True
    definitionInfoStr="<br/>".join(definitionInfoStack)

    sentenceMustHaveBold=True
    findNOBOLD=definitionInfoStr.find('NOBOLDINSENTENCES')
    if findNOBOLD>=0:
        sentenceMustHaveBold=False
        definitionInfoStr=re.sub(r'NOBOLDINSENTENCES','',definitionInfoStr)
        currHtml=currHtml

    for x in quoteSplitList:
        if definitionHtml is None:
            definitionHtml=x
        else:
            if expectExample:
                exampleHtml=x

                if len(exampleHtml)<15:
                    raise ValueError("example sentence implausibly short (len=%d), example=\"%s\"\ncurrHtml=%s" % (len(exampleHtml),exampleHtml,currHtml.encode('ascii','backslashreplace')))
                if len(definitionHtml)<10:
                    raise ValueError("definition stuff implausibly short: %s\ncurrHtml=%s "% (definitionHtml,currHtml.encode('ascii','backslashreplace')))
                
                definitionStuff=definitionInfoStr
                if len(definitionStuff)>0:
                    definitionStuff += "<br/>"
                definitionStuff += definitionHtml

                definitionStuff += "<br/><a href=\"%s#bullet%d\">lookup</a>" % (url,bulletId);
                
                if debugCardData: print("definitionStuff=%s\nexample=%s\n\n" % (definitionStuff,exampleHtml))

                if sentenceMustHaveBold and exampleHtml.find('<b>')==-1:
                    raise ValueError("the sentence \"%s\" has no <b> in it -- did you forget to bold the vocabulary?" % (exampleHtml))
                
                if exampleHtml in sentenceSeen:
                    raise ValueError("the sentence \"%s\" appears more than once.  I think this will confuse Anki.  You can make a trivial change to a sentence to make it unique (at least, I think that'll be sufficient)" % (exampleHtml))
                sentenceSeen[exampleHtml]=1

                # extract bold
                exampleHtmlNormalized=exampleHtml
                
                exampleHtmlNormalized=re.sub(r'<b>([ ,.\'\u2018]+)',r'\1<b>',exampleHtmlNormalized)
                exampleHtmlNormalized=re.sub(r'([ ,.\'\u2018]+)</b>',r'</b>\1',exampleHtmlNormalized)
                exampleHtmlWithBlanks="";
                boldStringList=[]
                matchList=[]
                prevEnd=0
                #matchList=re.finditer(r'<b>([^<]+)</b>',exampleHtml)
                #matchList.append(('',len(exampleHtml),0)) # sentinel, so we don't have to handle
                for match in re.finditer(r'<b>([^<]+)</b>',exampleHtmlNormalized):
                    string=match.group(1)
                    first=match.start(0)
                    last=match.end(0)

                    string=re.sub(r'(\w+)/(\w+)',r'\1 / \2',string) # treat '/' as separate element

                    orig_thisBoldList=re.split(r' +',string)
                    thisBoldList=[]
                    thisBlankList=[]
                    for bold in orig_thisBoldList:
                        isBlank=True
                        if bold=='/':
                            isBlank=False
                        if isBlank:
                            if bold=="":
                                raise ValueError("bolded text led to a zero-length word from sentence \"%s\"" % (exampleHtmlNormalized))
                            if re.search(r'[^\]\[\w ]',bold,re.UNICODE) and bold!="geb'" and not(re.match(r'dieser ein, f.nf und zehn Minuten nach der Entbindung durchzuf.hrenden Beurteilung',string)):
                                charCodes=" ".join([str(ord(x)) for x in bold])
                                raise ValueError("bolded element \"%s\" from bolded text stretch \"%s\" includes non-letter content. from sentence \"%s\". character codes=%s" % (bold,string,exampleHtmlNormalized,charCodes))
                            if re.match(r'^\W*$',bold,re.UNICODE) or bold==" ":
                                raise ValueError("bolded element \"%s\" from bolded text stretch \"%s\" does not have any letters. from sentence \"%s\". character codes=%s" % (bold,string,exampleHtmlNormalized,charCodes))
                            thisBoldList.append(bold)
                            thisBlankList.append('<b>____</b>');
                        else:
                            thisBlankList.append(bold)
                    boldStringList += thisBoldList
                    thisBlankListStr=" ".join(thisBlankList)
                    exampleHtmlWithBlanks += exampleHtmlNormalized[prevEnd:first]
                    prevEnd=last
                    exampleHtmlWithBlanks += thisBlankListStr
                    
                exampleHtmlWithBlanks += exampleHtmlNormalized[prevEnd:] # handle last one
                if True:
                    print("html=%s" % (exampleHtml))
                    print("     %s" % (exampleHtmlWithBlanks))
                    print(boldStringList)
                if sentenceMustHaveBold:
                    fillInBlankCardList.append([exampleHtmlWithBlanks,boldStringList])
                else:
                    # do nothing -- no point in doing fill-in-the-blanks if there aren't any blanks
                    pass
                
                cardList.append([exampleHtml,definitionStuff])
                expectExample=False
            else:
                if re.match(r'^ *, *$',x) or re.match(r'^ *$',x):
                    #print("separate quotes=%s" % (x))
                    pass # that's expected
                else:
                    raise ValueError("found unexpected text between examples.  I'm expecting just a comma.  Was: %s\ntext was %s" % (x.encode('ascii','backslashreplace'),currHtml.encode('ascii','backslashreplace')))
                expectExample=True
    if not expectExample and len(quoteSplitList)>1: # if there's no quotes, i.e., quoteSplitLen==1, then that's okay
        raise ValueError("bullet should end in a quote after an example.  It didn't.  bullet html was:\n%s" % (currHtml.encode('ascii','backslashreplace')))

    hasQuote=len(quoteSplitList)>1
    return hasQuote

def ProcessIlvl(prev_ilvl,ilvl,next_ilvl,debugLevel,cardList,fillInBlankCardList,sentenceSeen,definitionInfoStack,currHtml,htmlOut,url,bulletId):

    if abs(ilvl-next_ilvl)>1:
        raise ValueError("went directly from ilvl %d to %d (text is %s).  BTW, going directly from level 2 to 0 should be okay, but I didn't account for that in the code.  I've hacked around it, by shuffling definitions s.t. the one with level 2 is not the last definition." % (ilvl,next_ilvl,currHtml))

    if debugLevel: print("stack size=%d" % (len(definitionInfoStack)))
    if debugLevel: print("html=%s" % (currHtml))

    if ilvl>=0 and ilvl<=prev_ilvl:
        if debugLevel: print("pop")
        definitionInfoStack.pop()

    if ilvl==prev_ilvl-1: # backtrack a level
        if debugLevel: print("pop 2")
        definitionInfoStack.pop()

    # deal with HTML output
    #print("p,i,n=%d,%d,%d" % (prev_ilvl,ilvl,next_ilvl),file=htmlOut)
    if ilvl==-1: # skip preamble to document, before the bulleted list starts
        pass
    else:
        if ilvl==prev_ilvl: # we don't have to do anything
            pass
        else:
            if ilvl>prev_ilvl:
                for i in range(prev_ilvl,ilvl):
                    if i!=-1:
                        pass #print("<li>",file=htmlOut)
                    print("<ul>",file=htmlOut)
            if ilvl<prev_ilvl:
                for i in range(ilvl,prev_ilvl):
                    print("</ul>",file=htmlOut)
                #print("<li>",file=htmlOut)

        print("<li><a name=\"bullet%d\">" % (bulletId),file=htmlOut)
        print(currHtml,file=htmlOut)
        print("</a></li>",file=htmlOut)

    if ilvl>=0: # i.e., not -1
        if debugLevel: print("HandleBulletText (stack size=%d)" % (len(definitionInfoStack)))
        if debugLevel:
            if ilvl!=len(definitionInfoStack):
                raise ValueError("stack size wrong ilvl=%d != len(definitionInfoStack)=%d" % (ilvl,len(definitionInfoStack)))
        hasQuote=HandleBulletText(cardList,fillInBlankCardList,sentenceSeen,definitionInfoStack,currHtml,url,bulletId)

        if not hasQuote and ilvl>=next_ilvl:
            raise ValueError("text didn't have example sentence, but it's a leaf: %s" % (currHtml))

        if debugLevel: print("push")
        definitionInfoStack.append(GetStringUpToFirstQuote(currHtml))
    else:
        hasQuote=True

    return hasQuote

parser = argparse.ArgumentParser('parse my idiosyncratic list of German words, so that AnkiWeb or Memrise can use it (not sure which yet)')
parser.add_argument("inFileName", help="the .docx file with my weird format",type=str)
parser.add_argument("outFileName", help="output file that can be imported into Anki",type=str)
parser.add_argument("htmlFileName", help="output HTML file for looking things up on the web",type=str)
parser.add_argument("--url",dest="url",help="URL of the HTML document for looking things up",type=str)
parser.add_argument("--numChoices",dest="numChoices",help="number of choices to generate for multiple-choice, fill-in-the-blanks",type=int,default=4)
args = parser.parse_args()

inFileName=args.inFileName
outFileName=args.outFileName
htmlFileName=args.htmlFileName
url=args.url

# get the .xml from the Word Doc and parse it
docxFile=zipfile.ZipFile(inFileName)
xml=docxFile.read('word/document.xml')
xmlTree = ElementTree.fromstring(xml)

if False:
    for elem in xmlTree.iter():
        print("next")
        print(elem.tag)
        if elem.attrib:
            print(elem.attrib)
        if elem.text:
            print(elem.text)
        if elem.tail:
            print(elem.tail)

# we only care about tags: ilvl, t, b
tagPrefix=str("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}")

ilvlSeen={}

sentenceSeen={}
cardList=[]
fillInBlankCardList=[]
definitionInfoStack=[]
currHtml=""

with open(htmlFileName,"w",encoding="utf-8") as htmlOut:
    # <meta http-equiv=\"content-type\" content=\"text/html; charset=utf-8\">
    print("<html><head><meta charset=\"utf-8\"><title>Deutsche W&umlo;rter</title></head><body>",file=htmlOut)

    ilvl=-1
    prev_ilvl=-1
    nextIsBold=False
    prev_hasQuote=False
    bulletId=0
    for elem in xmlTree.iter():
        bulletId += 1
        
        tag=elem.tag
        tag=re.sub(tagPrefix,'w:',tag) # get the tags back to the original form, which was easier to work with

        if tag=='w:ilvl':
            # note: when we see the ilvl tag, we're ready to process the _previous_ bullet, and get set up for the next one at the new bullet indent level
            attribName=tagPrefix+'val'
            ilvlRaw=elem.get(attribName)
            if ilvlRaw is None:
                raise ValueError()
            next_ilvl=int(ilvlRaw)
            if debugLevel: print("level=%d --> %d --> %d" % (prev_ilvl,ilvl,next_ilvl))

            hasQuote=ProcessIlvl(prev_ilvl,ilvl,next_ilvl,debugLevel,cardList,fillInBlankCardList,sentenceSeen,definitionInfoStack,currHtml,htmlOut,url,bulletId)


            prev_ilvl=ilvl
            ilvl=next_ilvl
            ilvlSeen[ilvl]=1
            currHtml=""
            prev_hasQuote=hasQuote

        if tag=='w:t':
            if ilvl is not None:
                #print("text (%s):%s" % ("bold" if nextIsBold else "    ",elem.text))
                html=textToHtml(elem.text)
                if nextIsBold:
                    html="<b>"+html+"</b>"
                currHtml += html

                nextIsBold=False
        if tag=='w:b':
            nextIsBold=True

    next_ilvl=ilvl # should work, doesn't really matter
    hasQuote=ProcessIlvl(prev_ilvl,ilvl,next_ilvl,debugLevel,cardList,fillInBlankCardList,sentenceSeen,definitionInfoStack,currHtml,htmlOut,url,bulletId)

    print("</body></html>",file=htmlOut)

    # cardList is a list of cards.  Each card is a list of [example-sentence-html , definition stuff]

    #print(ilvlSeen.keys())

    with open(outFileName, 'w', newline='', encoding='utf-8') as csvFile:
        importCsv = csv.writer(csvFile, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        for sentence,definition in cardList:
            importCsv.writerow([sentence,definition])

    if False: # takes a lot of space
        print("fill-in-the-blank debug data:")
        print(fillInBlankCardList)
    allBlankList=sorted(list(set(itertools.chain.from_iterable([boldList for sentence,boldList in fillInBlankCardList])))) # sorting isn't important, but useful for me to make sure
    #print(allBlankList)
    uppercaseBlankList=[x for x in allBlankList if x[0].isupper()]
    lowercaseBlankList=[x for x in allBlankList if x[0].islower()]
    
    # output fill-in-the-blank data
    # not yet implemented
    # need to do something so that the sentences are consistent, otherwise every time I generate it, it'll get different random distractors
    # plan: save everything into stableFillInTheBlanksFileName, later look up what we already had, and make sure we get that again for each sentence
    print("\ndealing with fill-in-the-blank stuff, not yet really implemented")
    stableFillInTheBlanksFileName=inFileName + ".fill-in-the-blank-stable.tab" # cards we've already generated, so that we always re-do them
    fillInTheBlanksOutFileName=outFileName+".fill-in-the-blanks.tab"
    # okay, read the previous stuff, so we know about sentences that already exist
    stableSentenceToChoiceList={}
    if os.path.isfile(stableFillInTheBlanksFileName):
        with open(stableFillInTheBlanksFileName,'r',newline='',encoding='utf-8') as stableFillInTheBlanksFile:
            stableCsv=csv.reader(stableFillInTheBlanksFile, delimiter='\t', quotechar='\"')
            for line in stableCsv:
                sentence=line.pop(0)
                choiceList=line
                stableSentenceToChoiceList[sentence]=choiceList
    # now make a new file of sentence/choices, while forcing previously existing sentences to conform to the old stuff
    with open(fillInTheBlanksOutFileName,'w',newline='',encoding='utf-8') as fillInTheBlanksOutFile: # first do into outFileName, so we don't screw up the stable file if there's a problem
        fillInTheBlanksOutFileCsv=csv.writer(fillInTheBlanksOutFile,delimiter='\t',quoting=csv.QUOTE_MINIMAL)
        for sentence,correctWordList in fillInBlankCardList:

            choiceList=[]
            if sentence in stableSentenceToChoiceList:
                choiceList=stableSentenceToChoiceList[sentence]
            else:
                numDetractors=args.numChoices-1
                correctWordSet=set(correctWordList)
                wordListList=[correctWordList] # first is always correct
                for detractor in range(0,numDetractors):
                    wordList=[]
                    for correctWord in correctWordList: # make same number detractor words
                        while True:
                            if correctWord[0].isupper():
                                word=SelectWord(uppercaseBlankList)
                            else:
                                word=SelectWord(lowercaseBlankList)
                            if word not in correctWordSet: # don't pick something that's correct, even if in the wrong position.  however, we can pick a different conjugation/declension of a correct word -- that's not ideal, but too much of a hassle to avoid to be worth it
                                break
                        wordList.append(word)
                    wordListList.append(wordList)
                choiceList=[" , ".join(x) for x in wordListList]
                output=[sentence] + choiceList
                fillInTheBlanksOutFileCsv.writerow(output)
                
    shutil.copyfile(fillInTheBlanksOutFileName,stableFillInTheBlanksFileName)
            
    print("\nread %d example sentences / cards" % (len(cardList)))
