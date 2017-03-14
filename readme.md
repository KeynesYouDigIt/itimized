#itimizer is a lightweight item catalog

##contributing
1. clone
2. (optional) create a virtual environment

3. Run `pip install requirements.txt`

you may need to run `sudo apt install libpq-dev python-dev` to make sure the server can work with psycopg2, the ORM adapter for Postgres.

3. Create a postgres database and note the name, username and password
    and add an enviromental variable
    DATABASE_URL equal to postgresql://user:password@localhost:5432/DBNAME.
    To do this use the set command in windows and export for bash,
    and add these commands to the begining of
    the activate script in your virtual enviroment,
    which should not push to github with the source code.


    For example, the last line of the "C:\\...path...\\venv_Vasco\\Scripts\\activate.bat"
    script in my virtual enviroment reads
    `set "DATABASE_URL=postgresql://user:password@localhost:5432/DBNAME"`

4. run `python main.py runserver`

site should now be running on localhost.

###########
#Information on the AWS server this app is deployed on

This README.md file should include all of the following:
i. The IP address and SSH port so your server can be accessed by the reviewer.

54.236.42.128

ii. The complete URL to your hosted web application.
http://54.236.128/login

iii. A summary of software you installed and configuration changes made
UFW, Apache2, Mod_wsgi, git, everything in requirements.txt


changed several configurations in
/var/www/html/hitWSGI.wsgi
/etc/apache2/sites-available/000-default.conf


iv. A list of any third-party resources you made use of to complete this project.


https://help.ubuntu.com/community/UFW

http://flask.pocoo.org/snippets/8/

http://modwsgi.readthedocs.io/en/develop/user-guides/configuration-guidelines.html
