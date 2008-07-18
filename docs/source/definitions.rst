.. rst3: filename: definitions.rst

.. _definitions:

==========================
Definitions
==========================

Introduction & Concepts
+++++++++++++++++++++++

GoFlow is an "activity based" workflow. Workflow processes are implemented as a set of activities that must be completed to achieve some result. In GoFlow, the logic of activities lies in python view scripts. The presentation consists of a django (or any other kind of) template. GoFlow provides three main modules: 

    * Workflow API, 
    * Workflow Runtime
    * Workflow Admin.

Definitions
+++++++++++

Process
*******

A process is defined as a set of activities that must be done to achieve some goal. Business interactions are mapped to GoFlow processes to automate them. Process activities are connected using transitions defining what has to be done after each activity is completed.

Activity
********

An activity is a task that must be completed as a part of a process. In GoFlow activities are mapped to python scripts. This way an activity can do anything that can be done from a python script.

Transitions
***********

Transitions defines which activity or activities come before an activity is executed and after it is completed.

Role
****

Roles define who can perform an associated activity. Roles are defined at a per-process level.

ProcessInstance
***************

An instance is an occurrence of a process being executed. An instance is created when a process is started. The instance passes through the process activities until the process is terminated.

WorkItem
********

A workitem is added to the instance when an activity is completed. Workitems thus represent completed activities.

Activity Types
++++++++++++++

GoFlow defines seven basic activity types that can be used to design a process. They are:

    * Start
    * End
    * Activity
    * Switch
    * Split
    * Join
    * Standalone

Start Activity
**************

Start activities
--------------------
	Start activities are represented using a circle. Every process must have at least one start activity. Start is the only activity type that can be executed without the presence of an instance in the activity because instances are created when a start activity is executed. Processes with many start activities are awkward but possible in GoFlow. No transitions can lead to a start activity and only one outgoing transition is allowed per start activity.

End Activity
************

The end activity represents the end of a process. When an instance reaches the end activity the process is considered completed. Process must have exactly one end activity. This doesn√¢‚Ç¨‚Ñ¢t mean that processes can√¢‚Ç¨‚Ñ¢t end in different ways, since the end activity represents only that the process ends. How the process ends depends on the activities visited before the end activity. The end activity is represented in GoFlow using a double circle. The end activity can have many inbound transitions. Outbound transitions are not allowed.


Rules: Valid processes must have at least one begin activity and exactly one end activity. There must be at least one path leading from a start activity to the end activity.

Normal Activity
***************

Normal activities don√¢‚Ç¨‚Ñ¢t have a special meaning so they are used to represent tasks that should be done as a part of a process. A rectangle is used to represent these activities. Normal activities can receive many inbound transitions but can only have one outbound transition.

Switch Activity
***************

A switch activity represents a point of decision in a process. Instances reaching a switch activity are evaluated and depending on some conditions the instance can be routed to different activities. Switch activities can have many inbound transitions and many outbound transitions. Switch activities are represented using a diamond.

Split Activity
**************

Sometimes two or more activities in a process can be done independently in parallel. A split activity is used to split an instance and route it to many activities. This way an instance can be in many activities at the same time. Split activities represent subflows in a workflow. A split activity can receive many inbound transitions and can have many outbound transitions. Split activities are represented by a triangle.

Join Activity
*************

A join activity is used to regroup instances splitted from a split activity. When an instance reaches a join activity the engine verifies that the instance is present also in some other activity. If so, the instance must wait in the join activity until all activities leading to the join activity are completed. Once all activities reach the join activity the instance can be directed to the next activity. Join activities can have many inbound transitions (more than one is expected) and can only have one outbound activity. Join activities are represented using an inverted triangle.

Standalone Activity
*******************

Standalone activities are represented by hexagons. A standalone activity is not part of the normal flow of the process so they are not related to instances. A standalone activity can be executed any time by an user with the required permissions. These activities are ideal for data management related to the process, listings, adding items, removing items, etc. Many processes can be designed as a set of standalone activities if there's no order relationship between the different activities in the process. Other processes consist of a main process flow and a set of auxiliary standalone activities. Standalone activities can√¢‚Ç¨‚Ñ¢t have inbound nor outbound transitions.

AutoRouting & Interactiveness
+++++++++++++++++++++++++++++

AutoRouting
***********

When an activitiy is completed the engine may or may not automatically route the instance to the next activity in the process. Activities with the "AutoRouting" setting activated automatically route the instance to the next process activity when the activity is completed. If the activity is not "AutoRouting" the user must "send" the activity after completion to let the instance continue. This can be used in activities where the user can edit information and review it many times before deciding that the activity is completed.

Interactiveness
***************

In GoFlow activities can be automatic or interactive. Interactive activities are activities that require some kind of interaction from the user. These activities usually present a form asking the user to fill some data. After the information is submitted the activity is completed. Automatic activities in contrast are executed automatically by the GoFlow engine without any user interaction. Frequently automatic activities are hidden from the user view of a process.

    * Auto-routed activities have red arrows going out of them.
    * Non-auto-routed activities have black arrows going out of them.
    * Interactive activities have blue borders.
    * Automatic activities have black borders.

Sample Process
++++++++++++++

The picture on the left shows the graph of a process. This process defines requests to a shared CD collection. The start activity (interactive) is where the user picks a CD. Then the manager must verify that the CD is available in the "Approve loan" activity. If the CD is available, the manager sends the CD to the user, and the request is accepted. If not, the request is rejected. The standalone activity "Browse CDs" can be used by the user or the manager to browse the CD collection.

Modules
+++++++

GoFlow defines three modules:

    * The Process Manager
    * The User Interafce
    * The Process Monitor

Process Manager
***************

The process manager is the module used to create and modify processes. This module is normally used by an administrator and process designers to create processes. The process manager covers the following functionality:

    * Create process and process versions
    * Create, rename, edit and delete activities
    * View a graph of the process activities
    * Check if a process is valid
    * Activate/de-activate a process
    * Edit the source code of activities (python scripts) and templates (Smarty templates)
    * Define roles and define what roles are allowed to execute what activities
    * Map users to roles
    * Export processes to XML files (backup)
    * Load processes from XML files (restore)

User Interface
**************

The user interface is used by the users to browse processes where they can start new instances, or run activities to which their role has permissions and belong to a particular instance. Users can execute activities, and see the results and some statistics about work asssigned to them.

The Process Monitor
*******************

The process monitor is used to monitor and control the execution of processes. The following list shows some features of the process monitor API.

    * List processes, process activities and number of instances per activity
    * List active instances and exceptions
    * Browse instances and modify instance properties
    * Send instances to some activity
    * Assign or reassign an instance to some user
    * Abort instances
    * View statistics about completed processes, execution time, and time spent per activity

