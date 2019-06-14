import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-auth-lti',
    version='2.0.0',
    packages=['django_auth_lti'],
    include_package_data=True,
    license='TBD License',  # example license
    description='A simple Django app containing LTI auth middleware and backend.',
    long_description=README,
    url='http://tlt.harvard.edu/',
    author='Harvard University Teaching and Learning Technologies Program',
    author_email='tlt-ops@g.harvard.edu',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        "Django>=2.0",
        "ims-lti-py==0.6",
        "django-braces==1.3.1",
        "oauth2==1.9.0.post1",  # to catch errors uncaught by ims-lti-py
    ],
    tests_require=[
        'mock',
    ],
    zip_safe=False,
)
