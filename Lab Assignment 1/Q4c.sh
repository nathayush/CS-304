#!/bin/bash
sed -n 'n;n;p;' q4_c.txt | while read line; do
	if (( !($( echo $line | wc -w ) % 2) ));
	then
		echo $line
	fi
done
