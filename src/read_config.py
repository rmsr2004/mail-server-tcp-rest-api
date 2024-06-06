import configparser

def read_config():
	config = configparser.ConfigParser()

	# Read the configuration file
	config.read('config.ini')

	# Access values from the configuration file
	debug_mode = config.getboolean('General', 'debug')
	log_level = config.getboolean('General', 'log')
	db_name = config.get('Database', 'db_name')
	db_host = config.get('Database', 'db_host')
	db_port = config.get('Database', 'db_port')
	db_user = config.get('Database', 'db_user')
	db_password = config.get('Database', 'db_password')

	# Return a dictionary with the retrieved values
	config_values = {
		'debug_mode': debug_mode,
		'log_level': log_level,
		'db_name': db_name,
		'db_host': db_host,
		'db_port': db_port,
		'db_user': db_user,
		'db_password': db_password
	}
	return config_values

## End of read_config.py