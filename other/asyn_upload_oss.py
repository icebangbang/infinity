import math

import pymysql
from itertools import groupby
import hashlib
from sshtunnel import SSHTunnelForwarder
import snowflake.client
import json
import time
import requests
import oss2
import uuid
import datetime
import csv
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import threading

def request_method(third_order_id):
	print('%s request start' % third_order_id)
	request_url = 'https://api.mautunai.finboat.net/admin/orders/order/detail'
	data_search = {}
	data_search['_id'] = third_order_id
	request_body = json.dumps(data_search)
	headers = {
		'Content-Type': 'application/json',
		'Referer': 'https://mautunai.finboat.net/',
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
		'Cookie': 'access_token_cookie=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2MzQxNzMxMjAsIm5iZiI6MTYzNDE3MzEyMCwianRpIjoiMTM2NTM3YjYtOTE3Yy00NThlLWI2ODctZjg5NWZhMWZmNTI0IiwiZXhwIjoxNjM0MjA5MTIwLCJpZGVudGl0eSI6eyJ1aWQiOiI2MDQ1ODIyMDJiMzllMTRlZWY5NjE0MTQiLCJuYW1lIjoibWF1dHVuYWkiLCJwZmxhZyI6MCwicm9sZSI6Ilx1N2JhMVx1NzQwNlx1NTQ1OCJ9LCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MiLCJjc3JmIjoiM2JlZDQ5NTUtNDU4OC00ZDdjLTkxM2EtODg4Y2JkNDM1MGNlIn0.YhWTNrhVYgDjRr6SZ1Dj3tSQ7yrEKE8dhodiBEXo9eM; csrf_access_token=3bed4955-4588-4d7c-913a-888cbd4350ce'
	}
	response = requests.post(url=request_url, headers=headers, data=request_body)
	print('%s request end' % third_order_id)
	if response.status_code == 200:
		response_data = response.json()
		return response_data
	else:
		print('%s request error, %s' % (third_order_id, response.status_code))
	return None

def get_upload_url(face_img_url, user_cid, phone):
	print('%s, %s开始上传oos' % (user_cid, phone))
	# endpoint = 'http://oss-cn-hangzhou.aliyuncs.com'
	endpoint = 'http://oss-ap-southeast-5.aliyuncs.com'
	auth = oss2.Auth('LTAI5t7WPBhWD6seW835H9Ti', 'Bq1FrB88AI6Qut1D7iWBbgp22oFbAP')
	# bucket = oss2.Bucket(auth, endpoint, 'sake-storage-hz')
	bucket = oss2.Bucket(auth, endpoint, 'sake-storage')
	input = requests.get(face_img_url)
	sign_uuid = uuid.uuid1()
	img_path_key = str(sign_uuid)
	result = bucket.put_object(img_path_key, input)
	if result.status == 200:
		print('{} ,上传oss成功'.format(face_img_url))  # 打印上传的返回值 200成功
		# jpg_url = bucket.sign_url('GET', img_path_key, 300)  # 阿里返回一个关于Zabbix_Graph.jpg的url地址 60是链接60秒有效
		return sign_uuid
	else:
		print('{} ,上传oss失败'.format(face_img_url))
	return None

def upload_file(fileName, fileContent):
	# endpoint = 'http://oss-cn-hangzhou.aliyuncs.com'
	endpoint = 'http://oss-ap-southeast-5.aliyuncs.com'
	auth = oss2.Auth('LTAI5t7WPBhWD6seW835H9Ti', 'Bq1FrB88AI6Qut1D7iWBbgp22oFbAP')
	# bucket = oss2.Bucket(auth, endpoint, 'sake-storage-hz')
	bucket = oss2.Bucket(auth, endpoint, 'sake-storage')
	file_data = {}
	file_data['contact'] = fileContent
	result = bucket.put_object(fileName, json.dumps(file_data, ensure_ascii=False))
	if result.status == 200:
		print('{} ,上传oss成功'.format(fileName))  # 打印上传的返回值 200成功
		# jpg_url = bucket.sign_url('GET', img_path_key, 300)  # 阿里返回一个关于Zabbix_Graph.jpg的url地址 60是链接60秒有效
		return fileName
	else:
		print('{} ,上传oss失败'.format(fileName))
	return None

def convert_status(source_status):
	if source_status == 100:
		return 100
	elif source_status == 121:
		return 170
	elif source_status == 131:
		return 180
	elif source_status == 132:
		return 171
	else:
		return 200


once = 0
total = 0
pool = ThreadPoolExecutor(20)
semaphore = threading.Semaphore(20)

def upload_oss_and_write_file(new_item, type, test_count):
	global once, total
	semaphore.acquire()
	# print(test_count)

	# 报错重跑或者更新，需要加校验
	# is_exist = 0
	# with open('bid.csv', 'r') as oldBidFile:
	# 	reader = csv.DictReader(oldBidFile)
	# 	for row in reader:
	# 		if row['thirdparty_order_id'] == new_item['thirdparty_order_id']:
	# 			is_exist = 1
	# if is_exist == 1:
	# 	oldBidFile.close()
	# 	semaphore.release()
	# 	return
	# else:
	# 	print(new_item['user_cid'], new_item['phone'], new_item['thirdparty_order_id'])


	thirdpart_response_data = request_method(new_item['thirdparty_order_id'])

	if thirdpart_response_data != None:
		idcard_front_img = None
		live_img = None
		idcard_image_hand = None
		while (idcard_front_img == None) or (idcard_front_img == None) or (idcard_image_hand == None):
			idcard_front_img = get_upload_url(thirdpart_response_data['data']['idcard_image_front'], new_item['user_cid'], new_item['phone'])
			live_img = get_upload_url(thirdpart_response_data['data']['face_img_url'], new_item['user_cid'], new_item['phone'])
			idcard_image_hand = get_upload_url(thirdpart_response_data['data']['work_picture'], new_item['user_cid'], new_item['phone'])
			# time.sleep(1)
		address = thirdpart_response_data['data']['address']
		gender = thirdpart_response_data['data']['gender']
		birth_day = thirdpart_response_data['data']['birth_day']
		marital_status = thirdpart_response_data['data']['marital_status']
		month_income = thirdpart_response_data['data']['month_income']
		education = thirdpart_response_data['data']['education']
		# 避免只有一个联系人
		flag = 0
		for contact_info in thirdpart_response_data['data']['contact_info']:
			if flag == 0:
				emrg_contact_name_a = contact_info['emergencyName']
				emrg_contact_mobile_a = contact_info['emergencyPhone']
				emrg_contact_rel_a = contact_info['emergencyRelation']
				flag = flag + 1
			elif flag == 1:
				emrg_contact_name_b = contact_info['emergencyName']
				emrg_contact_mobile_b = contact_info['emergencyPhone']
				emrg_contact_rel_b = contact_info['emergencyRelation']
		flag = 0
		work_type = thirdpart_response_data['data']['work_type']
		company_name = thirdpart_response_data['data']['company_name']
		if work_type != None:
			has_work = 1
		if type == 0:
			with open('user_detail.csv', 'a+', newline='') as userFile:
				fieldnames = ['user_cid', 'phone', 'idcard_front_img', 'live_img', 'idcard_image_hand', 'address',
							  'gender', 'birth_day', 'marital_status', 'month_income', 'emrg_contact_name_a',
							  'emrg_contact_mobile_a', 'emrg_contact_rel_a', 'emrg_contact_name_b', 'emrg_contact_mobile_b',
							  'emrg_contact_rel_b', 'work_type', 'company_name', 'has_work']
				writer = csv.DictWriter(userFile, fieldnames=fieldnames)
				if once == 0:
					writer.writeheader()
					once = 1
				writer.writerow(
					{'user_cid': new_item['user_cid'], 'phone': new_item['phone'], 'idcard_front_img': idcard_front_img, 'live_img': live_img,
					 'idcard_image_hand': idcard_image_hand,
					 'address': address, 'gender': gender, 'birth_day': birth_day, 'marital_status': marital_status,
					 'month_income': month_income,
					 'emrg_contact_name_a': emrg_contact_name_a, 'emrg_contact_mobile_a': emrg_contact_mobile_a,
					 'emrg_contact_rel_a': emrg_contact_rel_a,
					 'emrg_contact_name_b': emrg_contact_name_b, 'emrg_contact_mobile_b': emrg_contact_mobile_b,
					 'emrg_contact_rel_b': emrg_contact_rel_b,
					 'work_type': work_type, 'company_name': company_name, 'has_work': has_work})
			userFile.close()

		device_info_file_name = "device/{}.json".format(new_item['thirdparty_order_id'])
		device_info_id = None
		other_order_id = thirdpart_response_data['data']['apply_list'][0]['_id']
		while device_info_id == None:
			device_info_id = upload_file(device_info_file_name, thirdpart_response_data['data']['contact'])
		with open('bid.csv', 'a+', newline='') as bidFile:
			fieldnames = ['thirdparty_order_id', 'device_info_id', 'other_order_id']
			writer = csv.DictWriter(bidFile, fieldnames=fieldnames)
			if once == 1:
				writer.writeheader()
				once = 2
			writer.writerow({'thirdparty_order_id': new_item['thirdparty_order_id'], 'device_info_id': device_info_id, 'other_order_id': other_order_id})
			total = total + 1
		bidFile.close()
		print('*第%s条迁移成功, %s, %s' % (total, new_item['user_cid'], new_item['phone']))
		print('---------------------------------------------------------------------------------------------------------------')
	else:
		print('requst error')
		semaphore.release()
	semaphore.release()

def confirm_data(cursor_rum, last_offset, page_size):
	global total, total

	last_time_sql = "SELECT * FROM ks_loan_order where status in('100','121','131','132','200') and  partner_code='{}' limit {},{}".format(
		'mautunai', last_offset, page_size)
	cursor_rum.execute(last_time_sql)
	source_list = cursor_rum.fetchall()
	# 多字段排序分组
	user_sort = sorted(source_list, key=lambda x: (x["user_cid"], x["phone"]))
	user_group = groupby(user_sort, key=lambda x: (x["user_cid"], x["phone"]))

	user_list = []
	for key, group in user_group:
		user_group_list = list(group)
		if len(list(user_group_list)) > 1:
			print(key[0], key[1])
			sort_list = sorted(user_group_list, key=lambda x: (x["gmt_create"]))
			latest_user = {}
			latest_user['user_po'] = sort_list[-1]
			latest_user['user_cid'] = key[0]
			latest_user['phone'] = key[1]
			user_list.append(latest_user)

	re = []
	test_count = 0
	for item in user_sort:
		new_item = list(filter(lambda x: (x['user_cid'] == item['user_cid'] and x['phone'] == item['phone']), user_list))
		insert_user_flag = 0
		if len(new_item) == 1 and new_item[0]['user_po']['gmt_create'] != item['gmt_create']:
			insert_user_flag = 1
		test_count = test_count + 1
		re.append(pool.submit(upload_oss_and_write_file, item, insert_user_flag, test_count))
	wait(re, return_when=ALL_COMPLETED)
	print('偏移量为%s模块内，根据身份证和手机号总共有%s组' % (last_offset, total))


def execute(cursor_rum):
	sql = "SELECT count(1) FROM ks_loan_order where status in('100','121','131','132','200') and partner_code='{}'".format(
		'mautunai')
	cursor_rum.execute(sql)
	source_count = cursor_rum.fetchall()
	# 分块读取，避免一次性读取大量数据
	page_size = 5000
	times = math.floor(int(source_count[0]['count(1)']) / page_size)
	print('一共有数据有%s条' % int(source_count[0]['count(1)']))
	start_time = datetime.datetime.now()  # 程序开始时间
	print('需要遍历，共有%s模块' % times)
	# last_count = int(source_count[0]['count(1)']) % page_size
	for i in range(0, times):
		offset = i * page_size
		print('--- 偏移量为%s ---' % offset)
		confirm_data(cursor_rum, offset, page_size)
		print('--- 第%s模块，完成 ---' % (i + 1))
	last_offset = times * page_size
	print('--- 最后偏移量为%s ---' % last_offset)
	confirm_data(cursor_rum, last_offset, page_size)
	over_time = datetime.datetime.now()  # 程序结束时间
	total_time = (over_time - start_time).total_seconds()
	print('#--- 迁移完成, %s ,用用时%s秒---#' % (total, total_time))


if __name__ == '__main__':
	# 开发环境
	# conn_rum = pymysql.Connect(
	# 	host='120.55.200.28',
	# 	port=3306,
	# 	user='ecreditpal', passwd='vaiFA3MQ9dLcDjWL',
	# 	db='rum', charset='utf8',
	# 	cursorclass=pymysql.cursors.DictCursor)
	# cursor_rum = conn_rum.cursor()
	#
	# execute(cursor_rum)
	#
	# cursor_rum.close()
	# conn_rum.close()

	# 生产环境
	with SSHTunnelForwarder(
			("52.184.8.192", 3007),
			ssh_username="lifeng.ye",
			ssh_pkey="~/.ssh/baipeng.pem",
			remote_bind_address=("rm-k1as78x4dp90382jt.mysql.ap-southeast-5.rds.aliyuncs.com", 3306),
			local_bind_address=("0.0.0.0", 1022)
	) as tunnel:
		conn_rum = pymysql.Connect(
			host='127.0.0.1',
			port=tunnel.local_bind_port,
			user='tropic', passwd='5pdUNJBoBW#GZldg',
			db='rum', charset='utf8',
			cursorclass=pymysql.cursors.DictCursor)

		cursor_rum = conn_rum.cursor()


		if not cursor_rum:
			raise (NameError, "连接数据库失败")

		execute(cursor_rum)
		cursor_rum.close()
		conn_rum.close()


