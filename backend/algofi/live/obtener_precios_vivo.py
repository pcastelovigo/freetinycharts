import os
from dotenv import dotenv_values
from algosdk import mnemonic
from algofi_amm.v0.asset import Asset
from algofi_amm.v0.client import AlgofiAMMMainnetClient
from algofi_amm.v0.config import PoolType, PoolStatus
from algofi_amm.utils import get_payment_txn, get_params, send_and_wait
from datetime import datetime
import requests
import json
import pickle
import mysql.connector
from mysql.connector import pooling
from multiprocessing.pool import ThreadPool as PISCINA


dbdiario = mysql.connector.pooling.MySQLConnectionPool(
	pool_name = "pumba2",
	pool_size = 24,
	host="localhost",
	user="pablo",
	password="test1",
	database="ALGOFIprecios_live"
	)

with open("/scripts/algofi/live/lista_vivo", "rb") as fp:
	lista_pares = pickle.load(fp)
with open("/scripts/algofi/decimales", "rb") as fp:
	decimales = pickle.load(fp)
decimales.update({0:6})
piscina_size = 16

class conexion(object):
	def __init__(self):
		codigo=""

my_path = os.path.abspath(os.path.dirname(__file__))
ENV_PATH = os.path.join(my_path, ".env")
user = dotenv_values(ENV_PATH)
user['mnemonic']="riot short artefact mammal similar daughter visual cute name hat arrive slim general review promote utility hollow squeeze level autumn manual better foil absorb doll"

sender = mnemonic.to_public_key(user['mnemonic'])
key =  mnemonic.to_private_key(user['mnemonic'])

amm_client = AlgofiAMMMainnetClient(user_address=sender)

def worker(elemento):
	try:
		ASSET_ID = elemento[0]
		ALGO_ID = elemento[1]
#		ASSET_ID = 137594422
#		ALGO_ID = 0
		try:
			unidades1 = (1 * pow(10,decimales[ASSET_ID]))/ (1*(pow(10,decimales[ALGO_ID])))
			unidades2 = (1 * pow(10,decimales[ALGO_ID])) / (1*(pow(10,decimales[ASSET_ID])))
		except KeyError:
		        unidades1 = (1 * pow(10,6))/ (1*(pow(10,6)))
		        unidades2 = (1 * pow(10,6)) / (1*(pow(10,6)))
		pass

		if ASSET_ID == 0:
			ASSET_ID = 1
		if ALGO_ID == 0:
			ALGO_ID = 1
		pool = amm_client.get_pool(PoolType.CONSTANT_PRODUCT_25BP_FEE,ASSET_ID, ALGO_ID)
		if pool.pool_status == PoolStatus.UNINITIALIZED:
			pool = amm_client.get_pool(PoolType.CONSTANT_PRODUCT_75BP_FEE,ASSET_ID, ALGO_ID)
		lppool = pool.address
		precioalgoXasa = pool.get_pool_price(ASSET_ID)
		precioasaXalgo = pool.get_pool_price(ALGO_ID)
		precioalgoXasa = precioalgoXasa * unidades2
		precioasaXalgo = precioasaXalgo * unidades1
		cantidad_asset1 = pool.asset2_balance
		cantidad_asset2 = pool.asset1_balance
		if ASSET_ID == 1:
			ASSET_ID = 0
		if ALGO_ID == 1:
			ALGO_ID = 0

		nombre_fichero2 = str(ASSET_ID) + "_" + str(ALGO_ID)
		ahora = datetime.now()
		fecha = ahora.strftime("%d/%m/%Y %H:%M")
		conexion = dbdiario.get_connection()
		cursor_vivo = conexion.cursor()
		sql = "CREATE TABLE IF NOT EXISTS %s (id INT AUTO_INCREMENT PRIMARY KEY, fecha VARCHAR(24) NOT NULL, precio VARCHAR(32) NOT NULL)" % nombre_fichero2
		cursor_vivo.execute(sql)
		conexion.commit()
		insercion = "INSERT INTO " + nombre_fichero2 + " (fecha, precio) VALUES (%s, %s)"
		valores = (fecha, precioasaXalgo)
		cursor_vivo.execute(insercion, valores)
		conexion.commit()
		sql = "select max(id) from %s" % nombre_fichero2
		cursor_vivo.execute(sql)
		result_set = cursor_vivo.fetchone()
		if result_set[0] > 250:
			borrar = result_set[0] - 250
			sql = ("delete from " + nombre_fichero2 + " where id < " + str(borrar))
			cursor_vivo.execute(sql)
			conexion.commit()
		cursor_vivo.close()
		conexion.close()

	except Exception as e:
		cursor_diario.close()
		conexion.close()
		print(e)
		pass

piscina = PISCINA(piscina_size)
for elemento in lista_pares:
	piscina.apply_async(worker, (elemento,))

piscina.close()
piscina.join()

