import compileall, sys

def addDependenciesToPath():
    sys.path.append('cronlp')
    sys.path.append('experiments')
    sys.path.append('gensim_mod')
    sys.path.append('pytopia')
    sys.path.append('file_utils')
    sys.path.append('stat_utils')
    sys.path.append('sys_utils')
    sys.path.append('logging_utils')

def compileDocTopicCoh():
    addDependenciesToPath()
    compileall.compile_dir('doc_topic_coh', force=1)

def compileAll():
    addDependenciesToPath()
    compileall.compile_dir('.', force=1)

if __name__ == '__main__':
    #compileDocTopicCoh()
    compileAll()
