# copy full paths of dep jars to one file, execute from palmetto folder
find "`pwd`/lib" -type f -name '*.jar' > depjars.txt
