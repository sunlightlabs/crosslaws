# Download and unzip all uscode files for 2011. 
DIR=~/data/
HERE=$PWD
DEST=$DIR"uscode.house.gov/zip/2011/"
mkdir -P $DIR
wget -m -l1 -P $DIR http://uscode.house.gov/zip/2011/
cd $DEST
for filename in `ls | xargs`; do unzip $filename; done
rm `find *.zip | xargs`
cd $HERE

