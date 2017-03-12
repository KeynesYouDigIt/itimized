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
