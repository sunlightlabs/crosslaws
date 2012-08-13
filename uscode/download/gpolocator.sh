# Download and unzip all uscode files for 2011.
# Run it from the uscode folder.
DIR=$PWD"/data"
DEST=$DIR"/uscode.house.gov/zip/2011/"
echo $DIR
echo $DEST
#mkdir -P $DIR
#wget -m -l1 -P $DIR http://uscode.house.gov/zip/2011/
cd $DEST
for filename in `ls | xargs`; do unzip $filename; done
rm `find *.zip | xargs`
cd $DIR
