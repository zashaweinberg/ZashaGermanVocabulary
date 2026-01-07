Anki: There are duplicates. For example, search for "Einkommen hinnehmen".  sort exported-decks.txt | uniq -c | sort -k 1,1n (I don't know why Anki doesn't get this) Maybe next time I should write a thing to only put in new things. Workflow: you export current cards, and a script compares the exports to the deutsche-woerter.tsv file and gets only the new ones.

ALSO: ask ChatGPT if it knows why AnkiWeb fails to notice the duplicates -- worth a shot


# ZashaGermanVocabular
For my personal German practice.

source test-deutsch-woerter.sh : test processing the Word doc, but don't update any official files.

source deutsch-woerter.sh : process the Word doc and update the list of words and the HTML for the web site (after 'git push'). After doing this, you must import deutsch-woerter.tsv to AnkiWeb

Importing to Anki
in Windows Anki App (make sure to synchronize the Android App, then the Windows App): Select 'import' (under 'File' menu).  Select the file 'deutsch-woerter.tsv'.
(all settings in the import dialog are actually the default)
'Field separator': 'Tab'
'Allow HTML in fields':  enable
(under 'Import options')
'Note Type': 'Basic'
'Deck': 'Default'
'Existing notes': 'Update'
'Match scope': 'Note type'
(under 'Field mapping')
Front: '1...'
Back: '2...'
Tags: (nothing)
Then click 'Import' button
(can just click past the next screen)

 (wasn't necessary 2025-01, see again) delete cards that get duplicated because Anki apparently doesn't notice they're the same.  see Google Doc "Neue-deutsche-Woerter", search for "cemile".
Then click 'Sync'
In AnkiDroid, While looking at "Stapeln", drag down to synchronize.


# older version of Anki app
in Windows Anki App (make sure to synchronize the Android App, then the Windows App): Select 'import' (under 'File' menu).  Select the file 'deutsch-woerter.tsv'.  'Fields separated by: Tab' should be selected.  'Update existing notes when first field matches' should be selected.  'Allow HTML in fields' should be checked.  Following should be in effect: 'Field 1 of file is: mapped to Front' and 'Field 2 of file is: mapped to Back'.  Then click 'Import'.
 (wasn't necessary 2025-01, see again) delete cards that get duplicated because Anki apparently doesn't notice they're the same.  see Google Doc "Neue-deutsche-Woerter", search for "cemile".
Then click 'Sync'
In AnkiDroid, While looking at "Stapeln", drag down to synchronize.

# OLD STUFF with apache at Uni-Leipzig
# If it's under apache, you might need to set the encoding to UTF-8 in the HTTP headers like so, in the .htaccess file for the relevant directory:
#<Files "deutsch-woerter.html">
#AddCharset UTF-8 .html
#</Files>
# BTW: this doesn't work on Chrome on Windows (it seems to display the file as if it were ASCII), but it does work on the Samsung browser on my phone, so good enough for me.
# scp /c/zasha/temp-away-from-work/deutsch-woerter.html ahvaz:public_html/
