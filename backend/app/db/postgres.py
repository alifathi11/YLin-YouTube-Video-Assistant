import psycopg2 
from pgvector.psycopg2 import register_vector

class PostgresDB:
	def __init__(self, dsn: str):
		self.conn = psycopg2.connect(dsn)
		self.conn.autocommit = True 

		register_vector(self.conn)

	def execute(self, query, params=None):
		with self.conn.cursor() as cur: 
			cur.execute(query, params)

	def fetchall(self, query, params=None):
		with self.conn.cursor() as cur: 
			cur.execute(query, params)
			return cur.fetchall()