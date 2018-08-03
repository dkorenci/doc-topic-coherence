from pytopia.tools.IdComposer import IdComposer
from pytopia.context.ContextResolver import resolve, resolveId

class Topic(IdComposer):
    '''
    Interface that a pytopia topic-like should support,
    plus a usable implementation.
    data: model - TopicModel, vector - ndarray or compatible object
    '''
    def __init__(self, model, topicId, vector=None):
        self.model = resolveId(model)
        self.topicId = topicId
        IdComposer.__init__(self, ['model', 'topicId'])
        self._vector = vector

    def _resolveModel(self):
        if not hasattr(self, '_model') or self._model is None:
            self._model = resolve(self.model)

    @property
    def vector(self):
        if not hasattr(self, '_vector') or self._vector is None:
            self._resolveModel()
            self._vector = self._model.topicVector(self._topicId)
        return self._vector
