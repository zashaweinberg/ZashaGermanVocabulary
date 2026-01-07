sort exported-decks.txt  | sed "s:/>:>:g" > b
sort deutsch-woerter.tsv | sed "s:/>:>:g" > a
diff -w a b
