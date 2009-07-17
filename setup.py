from setuptools import setup

setup(
    name='django-goflow',
    version='0.65-svn',
    description='Fork of the workflow management for the Django web framework',
    author='Eric Simorre',
    author_email='goflow@alwaysdata.net',
    url='http://code.google.com/p/goflow/',
    packages=['goflow', 'goflow.apptools', 'goflow.runtime', 'goflow.graphics', 'goflow.graphics2', 'goflow.workflow', 'goflow.apptools.templatetags', 'goflow.runtime.templatetags', 'goflow.workflow.templatetags', 'goflow.graphics2.templatetags'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD Licence',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
)
