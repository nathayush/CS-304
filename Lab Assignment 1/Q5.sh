#!/bin/bash
regex="^[a-z0-9!#\$%&^_~-]+(\.[a-z0-9!#\$%&^_~-]+)*@([a-z0-9]([a-z0-9]*[a-z0-9])?\.)+[a-z0-9]([a-z0-9-]*[a-z0-9])?\$"

inp="a@@b.f"
if [[ $inp =~ $regex ]] ; then
    echo "k"
else
    echo "not k"
fi
