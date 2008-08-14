from goflow.apptools.forms import BaseForm, StartForm

from models import SampleModel

class SampleModelForm(StartForm):
    ''' form for starting workflow
    '''
    def save(self, user, data=None, commit=True):
        ''' overriden for adding the requester
        '''
        obj = super(StartForm, self).save(commit=False)
        obj.user = user
        obj.save()
        return obj
    
    class Meta:
         model = SampleModel
         exclude = ('user', 'number')
