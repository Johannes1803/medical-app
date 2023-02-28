How to contribute
===================================

contributions are highly welcome! Before you begin, I would kindly ask you to read through the following.

Environment
--------------
This project uses `pipenv <https://pipenv.pypa.io/en/latest/>`_ for dependency management. Follow the website's instructions
to setup pipenv, then run `pipenv install --dev`. Thanks to pipenv's lockfile, dependency resolution should be a breeze.

Repository layout
------------------

::

    project
    ├── docs  -- The rendered html documentation
    ├── docs_src  -- The docs source
    ├── medical_app    -- the main application
        |── backend
            |── authentication -- authentication flask blueprint
            |── errors -- error handler flask blueprint and decorator
            |── main -- blueprint for core application
            |── models.py -- definition of sql tables via ORM
        |── frontend
            |── templates -- html templates for login mini frontend
    ├── migrations     -- alembic 'version control' for database schemas
    ├── config.py      -- config of flask, backend, auth-0, ...    
    └── tests          -- mirrors medical_app



Testing
--------------
This project uses pytest for unit testing. Each end point has at least one test, usually way more for non-successful conditions.
I rely on pytest's conftest.py to setup test configuration.

Code Hygiene
-------------

The code is ...

* pep8 compliant (checked via flake8)
* formatted homogeneously (formatted via black)
* imports are sorted (via isort)

Documentation
---------------

The documentation you are reading is built with sphinx and hosted on github pages.