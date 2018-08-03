CJAR=Palmetto.jar # jar being compiled
DEPLIST=depjars.txt # list of dependancies, one jar file per line
MODNAME=palmettonew # module name

INCLUDE=""
for f in `cat $DEPLIST`; do 
	INCLUDE="--include $f $INCLUDE"
done

# might be needed for some JDKs
# export JCC_JDK=/home/damir/software/jdk1.8.0_131/

# build jcc wrapper module
python -m jcc --jar $CJAR $CLASSPATH $INCLUDE --python $MODNAME --version 0.1.0 --use_full_names --shared --build --install
