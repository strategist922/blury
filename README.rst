============
Blury
============

Python application to blur faces and license plates on images.

Prerequisites
-------------

You will need the following things properly installed on your computer.

**linux**

* `Git <http://git-scm.com/>`_
* `Docker <https://docs.docker.com/engine/installation/>`_

Install on linux with docker
----------------

Run following commands::

  $ git clone <repository-url>
  $ cd blury
  $ make docker_build

**Use blury with docker**

Run following commands in your terminal::
  
  cd blury
  make docker_run

Development mode
----------------

You need to first install `anaconda <https://conda.io/docs/user-guide/install/download.html>`_ on your system.

Clone the repository::
  
  $ git clone <repository-url>

Create a virtualenv and install all packages::

  $ cd blury
  $ make create_environment

Install darkflow::

  $ source activate blury
  $ cd /tmp & git clone https://github.com/thtrieu/darkflow.git
  $ cd darkflow
  $ pip install -U .
  
Create the doc::

  $ cd blury/docs
  $ make html

Then open index.html file in docs/_build/html

You can find all fonctions and main script in poc_floutage/blury folder.
Blury class is stored in blury/lib.py file.
  
To run blury, run this command::

  $ python blury/main.py ./data/raw ./data/processed 0.25 2

Be sure to put all input images in blury/data/raw folder.

Install with pip
----------------

Install all packages in a virtual environment as in "Developement mode" part.
Then in your blury environment install blury with pip ::

  $ cd blury
  $ make psi
  
Now you can run "blury" command from anywhere on your computer::

  $ cd /tmp
  $ blury /path/to/raw_dir /path/to/processed_dir 0.25 2

Improvement
----------

Plate detection should be better. Train a specific model to detect licence plate on road is better than 
locate vehicule and blur the car's bottom.
