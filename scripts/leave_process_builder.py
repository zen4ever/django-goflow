import sys, os
sys.path.insert(0, '/Users/sa/Code/workspace/goflow-src')
os.environ['DJANGO_SETTINGS_MODULE'] = 'leavedemo.settings'

from process_builder import ProcessBuilder, User, log
from leavedemo.leave.models import Manager

# ------------------------------------------------------------------------------------
# Leave Process Builder for goflow.leavedemo.leave
# ------------------------------------------------------------------------------------

class LeaveProcessBuilder(ProcessBuilder):
    def add_managers(self, managers={}):
        for name in managers:
            user = User.objects.get(username=name)
            for item in managers[name]:
                category, user_list = item
                mgr, new = Manager.objects.get_or_create(user=user, category=category)
                log('manager', mgr)
                for username in user_list:
                    related_user = User.objects.get(username=username)
                    mgr.users.add(related_user)
                    log('%s.users' % mgr, related_user.username)
                mgr.save()


def test():    
    USERS = [
        #username,      email,                  password,   [role,...]
        ('admin',       'admin@company.com',    'open',     []), #TODO: add staff, superuser status
        ('auto',        'auto@company.com',     'a',        []),
        ('primus',      'primus@company.com',   'p',        ['employee', 'leave']),
        ('notarius',    'notarius@company.com', 'n',        ['secretary', 'employee', 'leave']),
        ('prefectus',   'prefectus@company.com','p',        ['manager', 'employee', 'leave']),
        ('socius',      'socius@company.com',   's',        ['secretary', 'employee', 'leave']),
        ('secundus',    'secundus@company.com', 's',        ['employee', 'leave']),
        ('tertius',     'tertius@company.com',  't',        ['employee', 'leave']),
        ('quartus',     'quartus@company.com',  'q',        ['employee', 'leave']),
    ]
    
    #RELATIONSHIP
    MANAGERS = {
        # user        category     [user, ...]
        'notarius': [('secretary', ['admin', 'prefectus', 'primus','secundus','socius'])],
        'prefectus':[('supervisor',['prefectus', 'primus', 'secundus', 'tertius','quartus', 'socius', 'notarius'])],
        'socius':   [('secretary', ['tertius','quartus', 'notarius'])],
    }

    ROLES = [
        # rolename, [(app_label, model_class, codename), ...]
        ('employee', [('workflow', 'Process', 'can_instantiate')]),

        ('leave', [('workflow', 'Process', 'can_instantiate')]),

        ('manager', [
                ('workflow', 'Activity', 'add_activity'),
                ('workflow', 'Activity', 'change_activity'),
                ('workflow', 'Activity', 'delete_activity'),
                ('workflow', 'UserProfile', 'add_userprofile'),
                ('workflow', 'UserProfile', 'change_userprofile'),
                ('workflow', 'UserProfile', 'delete_userprofile'),
                ('leave', 'Account', 'add_account'),
                ('leave', 'Account', 'change_account'),
                ('leave', 'Account', 'delete_account'),
                ('graphics2', 'ActivityPosition', 'add_activityposition'),
                ('workflow', 'Application', 'add_application'),
                ('workflow', 'Application', 'change_application'),
                ('workflow', 'Application', 'delete_application'),
                ('leave', 'LeaveRequest', 'add_leaverequest'),
                ('leave', 'LeaveRequest', 'change_leaverequest'),
                ('leave', 'LeaveRequest', 'delete_leaverequest'),
                ('leave', 'Manager', 'add_manager'),
                ('leave', 'Manager', 'change_manager'),
                ('leave', 'Manager', 'delete_manager'),
                ('workflow', 'Process', 'add_process'),
                ('workflow', 'Process', 'can_browse'),
                ('workflow', 'Process', 'can_instantiate'),
                ('workflow', 'Process', 'change_process'),
                ('workflow', 'Process', 'delete_process'),
                ('graphics2', 'ProcessImage', 'add_processimage'),
                ('graphics2', 'ProcessImage', 'change_processimage'),
                ('graphics2', 'ProcessImage', 'delete_processimage'),
                ('workflow', 'PushApplication', 'add_pushapplication'),
                ('workflow', 'PushApplication', 'change_pushapplication'),
                ('workflow', 'PushApplication', 'delete_pushapplication'),
                ('workflow', 'Transition', 'add_transition'),
                ('workflow', 'Transition', 'change_transition'),
                ('workflow', 'Transition', 'delete_transition'),
            ]
        ),

        ('secretary', [
            ('workflow','Process', 'can_instantiate'),
            # ('LeaveRequest', 'can_add'),
            ]    
        ),
    ]

    APPLICATIONS = {
        'checkstatus' : {'url': 'checkstatus', 
                        'parameters': {'ok_values':('OK: Forward to supervisor', 'Denied: Back to requester')}},

        'approvalform': {'url':'approvalform', 
                        'parameters': {'ok_values':('OK: Forward to secretary', 'Denied: Back to requester')}},

        'refine': {'url':'refine', 
                   'parameters': {'ok_values':('Re-request', 'Withdraw request')}},

        'hrform': {'url':'hrform', 'parameters': None},

        'finalinfo': {'url':'finalinfo', 'parameters': None}
    }

    ACTIVITIES = [
        # title         kind        pushapplication      application      astart,afinish, join, split, roles
        ('begin',      'standard', 'route_to_secretary', 'checkstatus',   False, True,  'and', 'xor', ['secretary']),
        ('approval',   'standard', 'route_to_supervisor','approvalform',  False, True,  'and', 'xor', ['manager']),
        ('refinement', 'standard', 'route_to_requester', 'refine',        False, True,  'xor', 'xor', ['employee']),
        ('updatehr',   'standard', 'route_to_secretary', 'hrform',        False, True,  'and', 'and', ['secretary']),
        ('end',        'dummy',    'route_to_requester', 'finalinfo',     False, False, 'xor', 'and', []),
    ]

    TRANSITIONS = [
        #((input,       output),        transition_name,       transition_condition)
        (('begin',      'approval'),   'send_to_approval',    'OK: Forward to supervisor'),
        (('begin',      'refinement'), 'send_to_refinement',  'Denied: Back to requester'),
        (('approval',   'updatehr'), 'request_approved',    'OK: Forward to secretary'),
        (('approval',   'refinement'), 'not_approved',        'Denied: Back to requester'),
        (('refinement', 'begin'),      're_request',          'Re-request'),
        (('refinement', 'end'),        'cancel_request',      'Withdraw request'),
        (('updatehr',   'end'),        'tell_employee',       None)
    ]

    # you can build it up it up bit by bit or as follows:
    builder = LeaveProcessBuilder(title='leave', description='Request Leave/Vacation')
    builder.add_applications(APPLICATIONS)
    builder.add_roles(ROLES)
    builder.add_users(USERS)
    builder.add_managers(MANAGERS)
    builder.add_activities(ACTIVITIES)
    builder.add_transitions(TRANSITIONS)
    builder.setup_all()
    builder.as_graph(to='workflow.dot')

test()

