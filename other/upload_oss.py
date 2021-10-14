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

def request_method(third_order_id):
	request_url = 'https://api.mautunai.finboat.net/admin/orders/order/detail'
	data_search = {}
	data_search['_id'] = third_order_id
	request_body = json.dumps(data_search)
	headers = {
		'Content-Type': 'application/json',
		'Referer': 'https://mautunai.finboat.net/',
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
		'Cookie': 'access_token_cookie=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2MzQwOTE5OTksIm5iZiI6MTYzNDA5MTk5OSwianRpIjoiNjBkOGMyNjAtMGQyNS00YjUwLTg3YzctYmRlYjM4OTM2ZTQwIiwiZXhwIjoxNjM0MTI3OTk5LCJpZGVudGl0eSI6eyJ1aWQiOiI2MDQ1ODIyMDJiMzllMTRlZWY5NjE0MTQiLCJuYW1lIjoibWF1dHVuYWkiLCJwZmxhZyI6MCwicm9sZSI6Ilx1N2JhMVx1NzQwNlx1NTQ1OCJ9LCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MiLCJjc3JmIjoiMDAyZmNkNzEtODQwNi00ODk1LThiZGItM2YyMjRkYTI4YWVhIn0.37yGmeiuIyFms9us9vfK51e0LJVRInY-bEVZx5m6evs; csrf_access_token=002fcd71-8406-4895-8bdb-3f224da28aea'
	}
	response = requests.post(url=request_url, headers=headers, data=request_body)
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
	print(input)
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



def confirm_data(cursor_rum, cursor_sake, conn_sake, total, last_offset, page_size):
	last_time_sql = "SELECT * FROM ks_loan_order where status in('100','121','131','132','200') and  partner_code='{}' limit {},{}".format(
		'mautunai', last_offset, page_size)
	cursor_rum.execute(last_time_sql)
	source_list = cursor_rum.fetchall()
	# 多字段排序分组
	user_sort = sorted(source_list, key=lambda x: (x["user_cid"], x["phone"]))
	user_group = groupby(user_sort, key=lambda x: (x["user_cid"], x["phone"]))
	group_count = 0
	once = 0
	for key, group in user_group:
		sort_list = sorted(list(group), key=lambda x: (x["gmt_create"]))
		new_item = sort_list[-1]
		group_count = group_count + 1

		thirdpart_response_data = request_method(new_item['thirdparty_order_id'])
		if thirdpart_response_data != None:
			idcard_front_img = get_upload_url(thirdpart_response_data['data']['idcard_image_front'], key[0], key[1])
			live_img = get_upload_url(thirdpart_response_data['data']['face_img_url'], key[0], key[1])
			idcard_image_hand = get_upload_url(thirdpart_response_data['data']['work_picture'], key[0], key[1])
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
			with open('user_detail.csv', 'a+', newline='') as userFile:
				fieldnames = ['user_cid', 'phone', 'idcard_front_img', 'live_img', 'idcard_image_hand', 'address',
							  'gender', 'birth_day', 'marital_status', 'month_income', 'emrg_contact_name_a',
							  'emrg_contact_mobile_a', 'emrg_contact_rel_a', 'emrg_contact_name_b', 'emrg_contact_mobile_b',
							  'emrg_contact_rel_b', 'work_type', 'company_name', 'has_work']
				writer = csv.DictWriter(userFile, fieldnames=fieldnames)
				if once == 0:
					writer.writeheader()
					once = 1
				writer.writerow({'user_cid': key[0], 'phone': key[1], 'idcard_front_img': idcard_front_img, 'live_img': live_img, 'idcard_image_hand': idcard_image_hand,
								 'address': address, 'gender': gender, 'birth_day': birth_day, 'marital_status': marital_status, 'month_income': month_income,
								 'emrg_contact_name_a': emrg_contact_name_a, 'emrg_contact_mobile_a': emrg_contact_mobile_a, 'emrg_contact_rel_a': emrg_contact_rel_a,
								 'emrg_contact_name_b': emrg_contact_name_b, 'emrg_contact_mobile_b': emrg_contact_mobile_b, 'emrg_contact_rel_b': emrg_contact_rel_b,
								 'work_type': work_type, 'company_name': company_name, 'has_work': has_work})


			for item in sort_list:
				device_info_id = "device/{}.json".format(item['thirdparty_order_id'])
				device_info_id = upload_file(device_info_id, thirdpart_response_data['data']['contact'])
				total = total + 1
				with open('bid.csv', 'a+', newline='') as bidFile:
					fieldnames = ['thirdparty_order_id', 'device_info_id']
					writer = csv.DictWriter(bidFile, fieldnames=fieldnames)
					if once == 1:
						writer.writeheader()
						once = 2
					writer.writerow({'thirdparty_order_id': item['thirdparty_order_id'], 'device_info_id': device_info_id})
				print('第%s条迁移成功, 状态是%s' % (total, convert_status(int(item['status']))))
				print('---------------------------------------------------------------------------------------------------------------')
	print('偏移量为%s模块内，根据身份证和手机号总共有%s组' % (last_offset, group_count))
	return total

def execute(cursor_rum, cursor_sake, conn_sake):

	total = 0
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
		total = confirm_data(cursor_rum, cursor_sake, conn_sake, total, offset, page_size)
		print('--- 第%s模块，完成 ---' % (i + 1))
	last_offset = times * page_size
	print('--- 最后偏移量为%s ---' % last_offset)
	total = confirm_data(cursor_rum, cursor_sake, conn_sake, total, last_offset, page_size)
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
	# conn_sake = pymysql.Connect(
	# 	host='120.55.200.28',
	# 	port=3306,
	# 	user='ecreditpal', passwd='vaiFA3MQ9dLcDjWL',
	# 	db='sake', charset='utf8',
	# 	cursorclass=pymysql.cursors.DictCursor)
	# cursor_sake = conn_sake.cursor()
	#
	# execute(cursor_rum, cursor_sake, conn_sake)
	# cursor_rum.close()
	# conn_rum.close()
	# cursor_sake.close()
	# conn_sake.close()

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

		conn_sake = pymysql.Connect(
			host='127.0.0.1',  # 测试环境
			port=tunnel.local_bind_port,
			user='tropic', passwd='5pdUNJBoBW#GZldg',
			db='sake', charset='utf8',
			cursorclass=pymysql.cursors.DictCursor)
		cursor_sake = conn_sake.cursor()

		if not cursor_rum:
			raise (NameError, "连接数据库失败")

		execute(cursor_rum, cursor_sake, conn_sake)
		cursor_rum.close()
		conn_rum.close()
		cursor_sake.close()
		conn_sake.close()
