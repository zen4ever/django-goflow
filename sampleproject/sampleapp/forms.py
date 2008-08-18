from goflow.apptools.forms import BaseForm, StartForm

from models import SampleModel

class SampleModelForm(StartForm):
    ''' form for starting workflow
    '''
    def save(self, user, data=None, commit=True):
        ''' overriden for adding the requester
        '''
        obj = super(StartForm, self).save(commit=False)
        obj.requester = user
        obj.save()
        return obj
    
    class Meta:
         model = SampleModel
         exclude = ('requester', 'number')

class SampleModelNumberForm(StartForm):
    ''' form for editing the field number
    '''
    class Meta:
         model = SampleModel
         exclude = ('date', 'requester', 'text')
