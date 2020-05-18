#!/bin/sh

echo "Starting update script on: `date`"
while true; do
	python update_twitter.py
	sleep 14400
done
