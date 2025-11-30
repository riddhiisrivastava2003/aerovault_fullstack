try:
	import pymysql
	pymysql.install_as_MySQLdb()
except Exception:
	# If PyMySQL is not installed, DB may use mysqlclient; ignore silently.
	pass
