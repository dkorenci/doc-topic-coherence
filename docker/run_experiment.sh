# folders with necessary py packages, mounted and added to pythonpath
code="/data/code/doc_topic_coherence"

# data folders mounted into container, see doc_topic_coh.setting
data="/data/resources/ /datafast/palmetto/"

# if permissions need to be restored
reclaim=""

IMAGE=doc_coherence

# add source folders to mount options and pythonpath
mount=""; pypath=""
for f in $code; do
    mount="$mount --mount type=bind,src=$f,dst=$f"
    pypath="$pypath:$f"    
done
# add data folders to mount options
for f in $data; do
    mount="$mount --mount type=bind,src=$f,dst=$f"
done
# setup env variables
env="--env PYTHONPATH=$pypath"

# user and group to which ownership of files created/modified 
# within the container (with root account) will be restored
origuser=damir 
waytorun=$1
if [ $waytorun == "-i" ]; then 
    # execute the container interactively
    docker run -t -i $mount $env $IMAGE
else # execute python script specified by parameters    
    runPath=$1; script=$2
    for p in $@; do 
        [ $p == "-c" ] && clearPyc=1
    done
    # clean compiled files
    if [ $clearPyc ]; then  
        echo 'cleaning *.pyc files from source folders'
        for f in $code; do 
            find $f -name "*.pyc" -delete 
        done
    fi
    
    # CREATE SCRIPT THAT WILL BE EXECUTED WITHIN THE CONTAINER
    entrypoint=entrypoint.sh
    startCode="cd $runPath ; python $script "
    echo "useradd damir" >> $entrypoint
    echo $startCode >> $entrypoint
    # deleting compiled files
    if [ $clearPyc ]; then          
        for f in $code; do 
            echo "find $f -name \"*.pyc\" -delete" >> $entrypoint
        done
    fi            
    # set folder permissions back to local user
    for f in $reclaim; do
        echo "chown -R damir:damir $f" >> $entrypoint
    done    
    #cat $entrypoint
    chmod +x $entrypoint
    
    # EXECUTE CONTAINER
    mount="$mount --mount type=bind,src=`pwd`,dst=/entrypoint"
    runCmd="/bin/bash /entrypoint/$entrypoint"
    docker run $mount $env $IMAGE $runCmd
    
    # cleanup
    rm $entrypoint # remove entrypoint script
fi
