#!/bin/bash
cat q3_words.txt | while read line;
do
  for word in $line
  do
    res=$(grep -o "$word" q3.txt | wc -l)
    echo "$word -> $res"
  done
done
