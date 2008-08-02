from leavedemo.leave.models import Account
from datetime import timedelta

def update_hr(workitem):
    ''' automated and simplistic version of hrform.
    
    
    '''
    instance = workitem.instance
    leaverequest = workitem.instance.content_object
    if leaverequest.reason_denial:
        raise Exception('denial reason is not empty')
    if leaverequest.dayStart > leaverequest.day_end:
        raise Exception('date error')
    delta = leaverequest.dayEnd - leaverequest.day_start
    nbjours = delta.days + 1
    account = Account.objects.get(user=instance.user)
    if account.days < nbjours:
        raise Exception('no days enough in user account.')
    account.days -= nbjours
    account.save()
    pass