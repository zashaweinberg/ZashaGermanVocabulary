*** TO DO:

- There are duplicates. For example, search for "Einkommen hinnehmen".  sort exported-decks.txt | uniq -c | sort -k 1,1n (I don't know why Anki doesn't get this) Maybe next time I should write a thing to only put in new things. Workflow: you export current cards, and a script compares the exports to the deutsche-woerter.tsv file and gets only the new ones.
- that doesn't quite work, because the URLs change.  I need to either (1) build up a map (probably tab-delim file) from the relevant information to the href number, or (2) make a hash of that key and store the stable hash.  It'd be nice if the codes don't change now, so that I don't have to update everything and generate more duplicates that I then have to manually kill.  the explicit .tab map would mean that I might be able to capture it, but not sure how easy.
- the Find Duplicates function works if you select 'front' as the field
- ask ChatGPT if it knows why AnkiWeb fails to notice the duplicates -- worth a shot

# ZashaGermanVocabular

For my personal German practice, based on the Word document Deutsche-Woerter.docx

## README.md

To convert to HTML (so it's easier to read):

source htmlify-README.sh
epiphany README.html &
   [or some other browser]


## Testing the Word document

source test-deutsch-woerter.sh : test processing the Word doc, but don't update any official files.

## Updating

* Export cards from Anki, for sanity checking
    * open Anki Windows app
    * menu: File/Export
    * Export format = Cards, Include = all decks (default), Include HTML is checked (default)
    * save exported file as anki-export.txt
* update files with Python script (processes the Word doc and updates list of words for import to Anki and also HTML for the web
    * assuming you exported anki-export.txt
    * python3 ProcessDeutschWoerter.py --ankiExport *anki-export.txt* --url https://zashaweinberg.github.io/ZashaGermanVocabulary/deutsch-woerter.html /c/zasha/work/zasha/Deutsche-Klasse/Deutsche-Woerter.docx deutsch-woerter.tsv deutsch-woerter.html
    * update HTML on web
        * HTML is hosted by github, so pushing the updates has the effect of updating the public HTML
        * git commit -a ; git push
    * SAFETY FIRST: delete the file anki-export.txt, so that I don't accidentally use it next time without actually exporting
        * rm anki-export.txt
* Importing to Anki
    * open Android App
    * synchronize in Android
    * open Windows Anki App
    * synchronize in Windows
    * menu: File/Import
        * Select the file 'deutsch-woerter.tsv'.
        * (all settings in the import dialog are actually the default)
        * 'Field separator': 'Tab'
	* 'Allow HTML in fields':  enable
	* (under 'Import options')
	    * 'Note Type': 'Basic'
	    * 'Deck': 'Default'
	    * 'Existing notes': 'Update'
	    * 'Match scope': 'Note type'
	* (under 'Field mapping')
	    * Front: '1...'
	    * Back: '2...'
	    * Tags: (nothing)
	* Then click 'Import' button
	* (can just click past the next screen)
* handle duplicates
    * in Windows Anki app
    * Click 'Browse'
    * menu Notes/Find Duplicates

 (wasn't necessary 2025-01, see again) delete cards that get duplicated because Anki apparently doesn't notice they're the same.  see Google Doc "Neue-deutsche-Woerter", search for "cemile".
Then click 'Sync'
In AnkiDroid, While looking at "Stapeln", drag down to synchronize.

## outdated instructions

older version of Anki app

in Windows Anki App (make sure to synchronize the Android App, then the Windows App): Select 'import' (under 'File' menu).  Select the file 'deutsch-woerter.tsv'.  'Fields separated by: Tab' should be selected.  'Update existing notes when first field matches' should be selected.  'Allow HTML in fields' should be checked.  Following should be in effect: 'Field 1 of file is: mapped to Front' and 'Field 2 of file is: mapped to Back'.  Then click 'Import'.
 (wasn't necessary 2025-01, see again) delete cards that get duplicated because Anki apparently doesn't notice they're the same.  see Google Doc "Neue-deutsche-Woerter", search for "cemile".
Then click 'Sync'
In AnkiDroid, While looking at "Stapeln", drag down to synchronize.

OLD STUFF with apache at Uni-Leipzig

# If it's under apache, you might need to set the encoding to UTF-8 in the HTTP headers like so, in the .htaccess file for the relevant directory:
#<Files "deutsch-woerter.html">
#AddCharset UTF-8 .html
#</Files>
# BTW: this doesn't work on Chrome on Windows (it seems to display the file as if it were ASCII), but it does work on the Samsung browser on my phone, so good enough for me.
# scp /c/zasha/temp-away-from-work/deutsch-woerter.html ahvaz:public_html/
