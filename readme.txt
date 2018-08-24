This package contains code of the experiments from the article
"Document-based Topic Coherence Measures for News Media Text"
https://doi.org/10.1016/j.eswa.2018.07.063
share link: https://authors.elsevier.com/a/1XWV13PiGT7grp
If you use the code for scientific research, please cite the original article. 

All the code is licensed under GNU Lesser General Public License, 
except for the Palmetto modified code and .jar in the 'palmetto' folder, 
which are licensed under GNU Affero General Public License. 

This package contains original code and code derived (minor source modifications) 
from two other projects: Palmetto (palmetto folder) and Gensim (gensim_mod folder). 

The companion dataset can be found at: https://github.com/dkorenci/doc-topic-coherence-data

*** Setting up the environment ***

This is Python 2.7 code, the code should work with the latest version of the
numpy/scipy ecosystem and other required libraries.
Gensim 0.12.4 is recommended as the serialized topic models were build with this version.
In order to run the experiments with word coherence measures, Palmetto jar
has to be wrapped as a python package via the jcc tool.
See the palmetto folder for more information.

Alternatively, you can build a docker container using the code in the 'docker' folder.

To run the experiments, the resources contained in the dataset package and the
resources linked from this package have to be downloaded and the variables in
the settings module have to point to the location of the resources.

*** Code pointers ***

Code of most of the experiments can be found in the 'doc_topic_coh.coherence' package:
The 'measure_evaluation' package contains the model selection,
as well as the quantitative experiments from the Section 4 and Section 5 of the articles.
The qualitative_analysis module contains the experiments from Section 5.3. 
The 'experiment' module contains the helper class for running the experiments.
The 'coherence_builder' module contains the factory for coherence functions.

The 'doc_topic_coh.topic_discovery' package contains experiments from Section 6.

Code for creation, saving and loading of the topic dataset is contained within the 'dataset' package.

*** Applying the document coherence measures to new datasets ***

First, create the basic resources for your experiment:
corpus, dictionary, text2tokens converter, topic model.
You can modify the existing classes or adapt your own classes
to the interfaces defined by the corresponding classes in pytopia package.
Then, create the context (map of ids -> resource objects) with the resources.
Finally, use the CoherenceFunctionBuilder to create coherence functions from the parameters.
All the intermediate resources, such as documents indexed with document-topic
proportions, will be created automatically if the objects adhere to the interfaces.
See the resources.pytopia_context and its uses for more information.

*** Dataset ***

Code for creation, saving and loading of the dataset is contained within the 'dataset' package.

The dataset of labeled topics is created by loading model topics and labeling them.
Model topics are loaded from serialized topic models from the context.
Topic labels are created from model topic annotations, in two steps.
The first step creates topic "features" from the topic descriptions and the table of semantic topics.
XML file residing in the topic model folders contains textual description of topics.
Sem.topic tables are xlsx tables that link model topics to semantic topics (concepts).
Descriptions and sem.topic tables are products of the model topic annotation process.
Topic features contain data relevant for topic categorization, these features
are somewhat dataset dependent as slightly different annotation conventions were used.
Labeling labels model topics, based on their features, as one of five classes:
theme (one semantic topic), theme_noise (one semantic topic + noise),
theme_mix (two or more semantic topics), theme_mix_noise , noise.
Note that, labeling in the context of the topic dataset refers to labeling with
these five more specific classes, not 0/1 coherence labels.
Coherence labels are created upon running the experiments by
converting 'theme' and 'theme_noise' to 1 (coherent) and other labels to 0 (incoherent).
Coherence labels of topics are created from topic categories:
theme or theme_noise are considered coherent.
The details of the process is described in the article section 4.1
