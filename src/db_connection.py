import psycopg2

# ********************************************************************************************** #
#  Connect to the database and disables autocommit                                               #
# ********************************************************************************************** #
def db_connection(config_vars):
    db = psycopg2.connect(
        user = config_vars['db_user'],
        password = config_vars['db_password'],
        host = config_vars['db_host'],
        port = config_vars['db_port'],
        database = config_vars['db_name']
    )
    db.autocommit = False
    return db

# End of db_connection.py