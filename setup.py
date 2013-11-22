import os
from setuptools import setup
from setuptools import find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'django-auth-lti',
    version = '0.1',
    packages = find_packages(),
    include_package_data = True,
    license = 'TBD License', # example license
    description = 'A simple Django app containing LTI auth middleware and backend.',
    long_description = README,
    url = 'http://icommons.harvard.edu/',
    author = 'Colin Murtaugh',
    author_email = 'colin_murtaugh@harvard.edu',
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires = [
        "Django>=1.6",
        "django-filter==0.7",
        "ims-lti-py==0.6",
    ],
    zip_safe = False,
)
