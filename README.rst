
.. image:: https://build.conwet.fi.upm.es/jenkins/buildStatus/icon?job=ckan_apinfresources
    :target: https://build.conwet.fi.upm.es/jenkins/job/ckan_apinfresources/

.. image:: https://img.shields.io/badge/license-AGPL%203.0-blue.svg?style=flat
    :target: https://opensource.org/licenses/AGPL-3.0
    :alt: License


=============
ckanext-apinf_resources
=============

This repository includes apinf_resources CKAN extension, which enables CKAN to be integrated with an instance
of `Apinf`_ in order to have service level information of the API instances providing datasets resources.

.. _Apinf: http://apinf.org/

This extension is only used for those dataset resources which are registered as a link, and uses Apinf APIs
in order to look for the Apinf site which includes the description of the involved service. If this page
is found, this plugin creates a link which allows users to access it in order to retrieve feedback, documentation,
API status, or backlog information about the service providing the particular dataset resource.


------------
Installation
------------

.. Add any additional install steps to the list below.
   For example installing any non-Python dependencies or adding any required
   config settings.

To install ckanext-apinf_resources:

1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

2. Install the ckanext-apinf_resources Python package into your virtual environment::

     pip install ckanext-apinf_resources

3. Add ``apinf_resources`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload


---------------
Config Settings
---------------

The current CKAN extension uses the following configuration settings: ::

    # Apinf resources configuration
    # URL of API Umbrella
    ckan.apinf_resources.umbrella_url = https://umbrella.docker:8443

    # API Key and Admin token used for accessing API Umbrella APIs
    ckan.apinf_resources.umbrella_key = Ato9cJGVCNc5gQwRAut3131CNojXOwhmMOjIKyxX
    ckan.apinf_resources.umbrella_token = sImknT9zQ75Gksw5XZ74KZvKMpnX7fmtqoVSrhGI

    # URL of Apinf
    ckan.apinf_resources.apinf_url = http://apinf.docker:3000

------------------------
Development Installation
------------------------

To install ckanext-apinf_resources for development, activate your CKAN virtualenv and
do::

    git clone https://github.com/FIWARE-TMForum/ckanext-apinf_resources.git
    cd ckanext-apinf_resources
    python setup.py develop
    pip install -r requirements.txt
    pip install -r dev-requirements.txt


-----------------
Running the Tests
-----------------

To run the tests, do::

    python setup.py nosetest

This command will also generate a nose and coverage XML report


---------------------------------
Registering ckanext-apinf_resources on PyPI
---------------------------------

ckanext-apinf_resources should be availabe on PyPI as
https://pypi.python.org/pypi/ckanext-apinf_resources. If that link doesn't work, then
you can register the project on PyPI for the first time by following these
steps:

1. Create a source distribution of the project::

     python setup.py sdist

2. Register the project::

     python setup.py register

3. Upload the source distribution to PyPI::

     python setup.py sdist upload

4. Tag the first release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.1 then do::

       git tag 0.0.1
       git push --tags


----------------------------------------
Releasing a New Version of ckanext-apinf_resources
----------------------------------------

ckanext-apinf_resources is availabe on PyPI as https://pypi.python.org/pypi/ckanext-apinf_resources.
To publish a new version to PyPI follow these steps:

1. Update the version number in the ``setup.py`` file.
   See `PEP 440 <http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers>`_
   for how to choose version numbers.

2. Create a source distribution of the new version::

     python setup.py sdist

3. Upload the source distribution to PyPI::

     python setup.py sdist upload

4. Tag the new release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.2 then do::

       git tag 0.0.2
       git push --tags
