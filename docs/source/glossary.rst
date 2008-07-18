.. rst3: filename: glossary.rst

.. _glossary:

=========
Glossary
=========


..  glossary::

Application
+++++++++++

PushApplication
+++++++++++++++

User
++++

Activity
++++++++

An activity is a task that must be completed as a part of a process. In GoFlow activities are mapped to python scripts. This way an activity can do anything that can be done from a python script.

Role
++++

Roles define who can perform an associated activity. Roles are defined at a per-process level.

Activity-based Workflow
+++++++++++++++++++++++

An activity-based workflow is a workflow that is centered around a set of activities that someone (or something) has to do.

A given process instance (an instance of a process definition) may have several active workitems, which are the "pending" work a given actor has to do. Once a workitem is completed, the process definition specifies what are the next activities, and thus what new workitems must be created.

The main concepts in the definition of a process for an activity-based workflow are:

    * activities
        * applications that describe work
        * sub-process that recursively describe another process
    * transitions, with guards, deciding what's next

Process
+++++++

A process is defined as a set of activities that must be done to achieve some goal. Business interactions are mapped to GoFlow processes to automate them. Process activities are connected using transitions defining what has to be done after each activity is completed.

Transitions
+++++++++++

Transitions defines which activity or activities come before an activity is executed and after it is completed.

Workflow
++++++++

A workflow is a model to represent real work for further assessment, e.g., for describing a reliably repeatable sequence of operations. More abstractly, a workflow is a pattern of activity enabled by a systematic organization of resources, defined roles and mass, energy and information flows, into a work process that can be documented and learned.

The term workflow is used in computer programming to capture and develop human to machine interaction. Workflow software aims to provide end users with an easier way to orchestrate or describe complex processing of data in a visual form, much like flow charts but without the need to understand computers or programming.

Workflow is a term used to describe the tasks, procedural steps, organizations or people involved, required input and output information, and tools needed for each step in a business process. 

A workflow approach to analyzing and managing a business process can be combined with an object-oriented programming approach, which tends to focus on documents and data. In general, workflow management focuses on processes rather than documents. 

A number of companies make workflow automation products that allow a company to create a workflow model and components such as online forms and then to use this product as a way to manage and enforce the consistent handling of work. For example, an insurance company could use a workflow automation application to ensure that a claim was handled consistently from initial call to final settlement. The workflow application would ensure that each person handling the claim used the correct online form and successfully completed their step before allowing the process to proceed to the next person and procedural step.

A workflow engine is the component in a workflow automation program that knows all the procedures, steps in a procedure, and rules for each step. The workflow engine determines whether the process is ready to move to the next step. 

Proponents of the workflow approach believe that task analysis and workflow modeling in themselves are likely to improve business operations.



related concepts: 

    * Petri-Nets: http://en.wikipedia.org/wiki/Petri_net

ProcessInstance
+++++++++++++++

An instance is an occurrence of a process being executed. An instance is created when a process is started. The instance passes through the process activities until the process is terminated.

WorkItem
++++++++

A workitem is added to the instance when an activity is completed. Workitems thus represent completed activities.

