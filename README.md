# OnePost
  Run the OnePost Server
# STEP 0:
  $ cd OnePostServer
# STEP 1: SET UP DATABASE
  $ sudo apt-get install sqlite3<br />
  $ cd OnePostServer<br />
  $ mkdir var<br />
  $ sqlite3 var/OnePost.sqlite3 < schema.sql
# STEP 2: INSTALL DEPENDENCIES
  $ python3 -m venv env<br />
  $ source env/bin/activate<br />
  $ pip install --upgrade pip<br />
  $ pip install -e .
# STEP 3: RUN THE SERVER
  $ source env/bin/activate<br />
  $ cd onepost<br />
  $ ./OnePostRun
# NOTICE
  Contact developer for facebook app permissions
