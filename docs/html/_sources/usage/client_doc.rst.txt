Medical Rest API documentation for clients
============================================


Rest API documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Find below the documentation of the medical app rest api. For even better user experience, I recommend opening
the file documentation/open_api3_spec.yaml file in interactive tools such as swagger hub, which allow you to send requests directly from within the UI.

`Rest api documentation <../_static/openapi3.html>`_.


Authorization
~~~~~~~~~~~~~~~~~~~~~

Login/Register to obtain an access token
------------------------------------------

The medical rest api uses auth-0 as external authentication platform. It uses JWT tokens for authorization.

In order to obtain a jwt token, go to `the startsite <https://medical-rest-api.onrender.com/>`_, where you login/register
via auth-0 and obtain the token. Be sure not to share it with anyone.

The authentication token must be included in the request header as follows::

    curl -X 'GET' \
    'https://medical-rest-api.onrender.com/medics/1/patients?limit=20' \
    -H 'accept: application/json' \
    -H 'Authorization: Bearer <my_secret_token>'


Role-based access control
----------------------------------

There are two roles defined, Medic and Patient.
These roles have priviliges associated with them. Refer to `Rest API documentation`_, to check which endpoint requires
which permission.

Medic:

* delete:medics -- Delete medic	
* write:medics -- Create and update medics	
* get:patients -- Read access to patients		
* get:records	-- Read access to medical records		
* write:records -- Create and update records
* delete:records -- Delete records	

Patient:

* get:patients -- Read access to patients
* write:patients -- Create and update patients
* delete:patients	Delete patient
* get:records	Read access to medical records
* delete:records -- Delete records	

Note that not all endpoints require to be logged in and some require to be logged in, but have no further permissions required.
To obtain one of the / both roles, reach out to me via email after registration.


Useful Links
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* `swaggerhub <https://swagger.io/tools/swaggerhub/>`_ for sending requests from a UI
* `jwt.io <https://jwt.io/>`_ for seeing the payload of your token