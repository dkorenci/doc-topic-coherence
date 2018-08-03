class ResourceBuilder():
    '''
    Class documenting interface for a pytopia resource builder.
    '''

    def resourceId(self, *args, **kwargs):
        '''
        If builder is to be cache-able, this method has to be implemented,
        since cache has to know the id of the resource to be built
        in order to perform the lookup.
        Params to this method must be the same as the params
        to build methods itself (__call__)
        '''
        return None

    def __call__(self, *args, **kwargs):
        ''' Build the resource. '''

from pytopia.tools.logging import resbuild_logger

@resbuild_logger
class SelfbuildResourceBuilder():
    '''
    Generic builder for resource classes that have .build() method, and are built
    by constructing the object and calling .build()
    '''

    def __init__(self, resourceClass):
        self.__resourceClass = resourceClass

    def __call__(self, *args, **kwargs):
        res = self.__resourceClass(*args, **kwargs)
        res.build()
        return res

    def resourceId(self, *args, **kwargs):
        res = self.__resourceClass(*args, **kwargs)
        return res.id
