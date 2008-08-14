from django.contrib.auth.models import User

def route_to_admin(workitem):
    '''route to admin
    this push application is a sample,
    the built-in push application "route_to_superuser"
    should be used instead
    '''
    return User.objects.get(username='admin')
