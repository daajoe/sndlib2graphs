#!/usr/bin/env bash

shpath="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

options=':hc:'
validate=""
while getopts $options option
do
    case $option in
	c)  validate="$OPTARG";;
        h)  error $EXIT $DRYRUN;;
	?)  printf "Usage: %s: [-c validate_path] path\n" $0
            exit 2;;
    esac
done

if [ -z "$validate" ]; then
    printf "No validation given.\n"
fi

shift $((OPTIND - 1))
path=$(realpath $1)

if [ ! -d "$path" ]; then
    printf "Directory does not exist. Exiting...\n"
    exit 2
fi

for file in $(find $path/*/*.xml -maxdepth 1 -type f) ; do 
    printf "Running sndlib2graphs for %s.\n" $file
    $shpath/sndlib2graphs.py $file
    if [ $? -ne 0 ] ; then
	#printf "Error on %s.\n Exiting.\n" $file >&2
	#rm $gr_file
	continue
	#exit 2
    fi
    continue
    outputfile=$path/gr/$(basename $file)
    for gr_file in $(find $outputfile*.gr -maxdepth 1 -type f) ; do
	if [ -n "$validate" ]; then
	    printf "Validate %s... " $gr_file
	    $validate/td-validate $gr_file
	    if [ $? -ne 0 ]; then
		printf "Deleting gr file %s" $gr_file
		continue
	    fi
	fi
    done;
done;
