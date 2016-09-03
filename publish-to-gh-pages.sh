#!/bin/bash
# execute from github repo root
cd "`dirname $BASH_SOURCE`"

# exit on error
set -e
set -o pipefail

# clone repo if not already cloned
[[ -d gh-pages ]] || (echo cloning repo && git clone git@github.com:CivMap/civmap.github.io.git gh-pages)

echo deleting old build
(cd gh-pages && find . ! -regex './.git.*' -delete)

# build
npm install

echo copying current build
cp --recursive --dereference static/* gh-pages/

# commit+push
hash_msg="`git log --oneline -1`"
cd gh-pages/
git add --all
git commit -m "build $hash_msg"
git push origin master

