#!/bin/bash

current=`python setup.py -V`

echo "Type the new version (current $current):"
read version

[[ -z $version ]] && echo 'Empty version, exiting...' && exit 1

sed -i '' -E "s/version='.+'/version='$version'/" setup.py

git ci setup.py -m "Bump to $version"
git tag $version
git push
git push --tags

echo "Commits between $version and $current:"
git log $version...$current --format='%Cgreen%h %Cred%cr %Creset%s %Cblue%cn%Cgreen%d'
