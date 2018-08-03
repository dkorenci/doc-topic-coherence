def cleanAll():
    from doc_topic_coh.settings import experiments_folder
    import shutil, os
    shutil.rmtree(experiments_folder)
    os.mkdir(experiments_folder)
    os.mkdir(os.path.join(experiments_folder, 'function_cache'))

def testModelSelection(type=None):
    from doc_topic_coh.coherence.measure_evaluation.model_selection import evaluateParamsOnDev
    evaluateParamsOnDev('run', subsample=3, type=type)

def testEval():
    from doc_topic_coh.coherence.measure_evaluation.evaluations import bestDocCohOnTest, wordCohOnTest
    #bestDocCohOnTest(10)
    wordCohOnTest(5)

def testEvalCro():
    from doc_topic_coh.coherence.measure_evaluation.evaluations_croelect import bestDocCohOnTestcro, bestWordCohOnTestcro
    #bestDocCohOnTestcro(20)
    bestWordCohOnTestcro(20)

def testEvalAll():
    cleanAll()
    testEval()
    testEvalCro()

def testAll():
    cleanAll()
    testModelSelection()
    testEval()
    testEvalCro()

if __name__ == '__main__':
    #testAll()
    #testEvalAll()
    cleanAll()
    #testEval()
    #testEvalCro()
    #testModelSelection(type='graph')
    #testModelSelection(type='distance')
    #testModelSelection(type='density')