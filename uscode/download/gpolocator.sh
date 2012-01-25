# Download and unzip all uscode files for 2010. 
mkdir -P ~/data/uscode/gpolocator
wget -m -l1 -nd  -P ~/data/uscode/gpolocator http://uscode.house.gov/zip/2010/
for filename in `ls | xargs`; do unzip $filename; done
rm `find *.zip | xargs`

