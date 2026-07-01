from app.db.postgres import PostgresDB
from psycopg2 import sql

class DBInitializer:
	def __init__(self, db: PostgresDB):
		self.db = db

	def run_schema(self, schema_path: str): 
		with open(schema_path, "r") as f: 
			sql_script = f.read()

		with self.db.conn.cursor() as cur:
			cur.execute(sql_script)