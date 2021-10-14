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

def request_method(third_order_id):
	request_url = 'https://api.mautunai.finboat.net/admin/orders/order/detail'
	data_search = {}
	data_search['_id'] = third_order_id
	request_body = json.dumps(data_search)
	headers = {
		'Content-Type': 'application/json',
		'Referer': 'https://mautunai.finboat.net/',
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
		'Cookie': 'access_token_cookie=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2MzQwMDY3OTgsIm5iZiI6MTYzNDAwNjc5OCwianRpIjoiMmEyNzAyMzQtYmNjYS00ZmI3LTg3OWQtZDdhYWYzODBhZmFmIiwiZXhwIjoxNjM0MDQyNzk4LCJpZGVudGl0eSI6eyJ1aWQiOiI2MDQ1ODIyMDJiMzllMTRlZWY5NjE0MTQiLCJuYW1lIjoibWF1dHVuYWkiLCJwZmxhZyI6MCwicm9sZSI6Ilx1N2JhMVx1NzQwNlx1NTQ1OCJ9LCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MiLCJjc3JmIjoiZjBjNGViMjAtNDVhZi00ODliLWFkMWQtNmRiMTQ4YzkxMzdlIn0.IEgJ75CzOnPGaqDFI32x6vlFEm3i2ChCpkZxEAkYVcI; csrf_access_token=f0c4eb20-45af-489b-ad1d-6db148c9137e'
	}
	response = requests.post(url=request_url, headers=headers, data=request_body)
	if response.status_code == 200:
		response_data = response.json()
		return response_data
	else:
		print('%s request error, %s' % (third_order_id, response.status_code))
	return None

def get_upload_url(face_img_url, third_order_id):
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

def convert_back_id(variable):
	if isinstance(json.loads(variable), int):
		bank_account_id = variable
	else:
		bank_account_id = json.loads(variable)['bank_id']
	return bank_account_id

def cal_time(target_time):
	now_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
	start = time.mktime(time.strptime(target_time, '%Y-%m-%d'))
	end = time.mktime(time.strptime(now_time, '%Y-%m-%d'))
	count_days = int((end - start) / (24 * 60 * 60))
	if count_days < 0:
		count_days = 0
	return count_days

def insert_bid(conn_sake, cursor_sake,item, new_user_id, bankcard_id, contact):
	bid_id = snowflake.client.get_guid()
	status = convert_status(int(item['status']))
	product_id = 200
	# bank_account_id = convert_back_id(item['debit_open_bank_id'])
	bank_account_id = bankcard_id
	amount = item['loan_amount']
	period = item['loan_term']
	cid = item['user_cid']
	mobile = item['phone']
	name = item['user_name']
	contract_no = item['thirdparty_order_id']
	other_order_id = item['thirdparty_order_id']
	latitude = item['latitude']
	longitude = item['longitude']
	ip_address = item['ip_address']
	bank_account_number = item['debit_bank_card']
	channel_name = item['channel_source']
	channel_label = item['channel_source']
	operate_time = item['review_time']
	deduct_time = item['loan_time']
	repayment_time = item['repayment_time']
	real_repayment_time = item['repaymented_time']
	# raise_amount
	# comment
	is_reloan =  int.from_bytes(item['is_reloan'], byteorder='little', signed=True)
	if item['expiry_time'] == None:
		is_overdue = 0
		overdue_days = 0
	else:
		is_overdue = 1
		overdue_days = cal_time(item['expiry_time'][0, 11])
	if int(item['status']) > 100:
		disburse_count = 1
	else:
		disburse_count = 0
	bid_creat_time = item['submit_time']

	device_info_id = "device/%s_%s.json" % (other_order_id, snowflake.client.get_guid())
	device_info_id = upload_file(device_info_id, contact)
	insert_bid_sql = "INSERT INTO `sake`.`bid`(`id`, `gmt_create`, `gmt_modified`, `status`, `user_id`, `saas_id`, `product_id`, `bank_account_id`, `amount`, `period`, `cid`, `mobile`, `name`, `contract_no`, `other_order_id`, `latitude`, `longitude`, `ip_address`, `bank_account_number`, `channel_id`, `channel_name`, `channel_label`, `operate_time`, `operator_id`, `deduct_time`, `repayment_time`, `real_repayment_time`, `is_reloan`, `is_overdue`, `overdue_days`,  `disburse_count`, `device_info_id`) " \
					 "VALUES ({}, '{}', '{}', {}, {}, 2237, {}, {}, {}, {}, '{}', '{}', '{}', '{}', '{}',  {}, {}, '{}', '{}', 2, '{}', '{}', '{}', 0, '{}', '{}', '{}', {}, {}, {}, {} ,'{}');".format(
		bid_id, bid_creat_time, bid_creat_time, status, new_user_id, product_id, bank_account_id, amount, period, cid, mobile, name, contract_no,
		other_order_id, latitude, longitude, ip_address, bank_account_number, channel_name, channel_label, operate_time,
		deduct_time, repayment_time, real_repayment_time, is_reloan, is_overdue, overdue_days, disburse_count, device_info_id
	).replace("'None',", "null,").replace("None,", "null,")
	cursor_sake.execute(insert_bid_sql)
	print(item['user_cid'] + ',' + item['phone'] + '，' + str(bid_id) + ', insert bid ok')

	if int(item['status']) > 100:

		bill_id = snowflake.client.get_guid()
		manage_fee = item['service_fee']
		if manage_fee == None:
			loan_amount = item['loan_amount']
		else:
			loan_amount = item['loan_amount'] - manage_fee
		daily_interest_rate = item['interest_rate']
		repayment_amount = item['loan_amount']
		repayment_interest = item['interest_amount']
		if repayment_interest == None:
			repayment_corpus = item['loan_amount']
		else:
			repayment_corpus = item['loan_amount'] - repayment_interest
		total_overdue_days = overdue_days
		overdue_manage_fee = item['expiry_amount']
		current_repayment_time = repayment_time
		current_repayment_amount = item['loan_amount']
		if int(item['status']) == 200:
			current_returned_amount = item['loan_amount']
		else:
			current_returned_amount = 0
		real_repayment_time = repayment_time
		real_repayment_corpus = repayment_corpus
		real_repayment_interest = repayment_interest
		real_repayment_amount = None
		if real_repayment_time == None:
			real_repayment_amount = repayment_amount
		real_repayment_overdue_fine = overdue_manage_fee

		insert_bill_sql = "INSERT INTO `sake`.`bill`(`id`, `gmt_create`, `gmt_modified`, `status`, `bid_id`, `other_order_id`, `user_id`, `product_id`, `saas_id`, `channel_id`, `deduct_time`, `deduct_operator`, `loan_amount`, `period`, `daily_interest_rate`, `manage_fee`, `repayment_time`, `repayment_amount`, `repayment_corpus`, `repayment_interest`, `total_overdue_days`,  `overdue_manage_fee`, `current_repayment_time`, `current_repayment_amount`, `current_returned_amount`, `real_repayment_time`, `real_repayment_corpus`, `real_repayment_interest`, `real_repayment_amount`, `real_repayment_overdue_fine`, `is_reloan`) " \
						  "VALUES ({}, '{}', '{}', {}, {}, '{}', {}, {}, 2237, 2, '{}', 0, {}, {}, {}, {}, '{}', {}, {}, {}, {}, {}, '{}', {}, {}, '{}', {}, {}, {}, {}, {});".format(
			bill_id, deduct_time, deduct_time, status, bid_id, other_order_id, new_user_id, product_id, deduct_time, loan_amount, period, daily_interest_rate,
			manage_fee, repayment_time, repayment_amount, repayment_corpus, repayment_interest, total_overdue_days, overdue_manage_fee,
			current_repayment_time, current_repayment_amount, current_returned_amount, real_repayment_time, real_repayment_corpus,
			real_repayment_interest, real_repayment_amount, real_repayment_overdue_fine, is_reloan
		).replace("'None',", "null,").replace("None,", "null,")
		cursor_sake.execute(insert_bill_sql)
		print(item['user_cid'] + ',' + item['phone'] + '，' + str(bid_id) + ', insert bill ok')

		payment_record_id = snowflake.client.get_guid()
		insert_payment_record_sql = "INSERT INTO `sake`.`payment_record`(`id`, `type`, `bank_account`, `bank_id`, `amount`, `status`, `bid_id`, `mobile`, `saas_id`, `channel_id`, `payment_channel`, `notify_time`) " \
		"VALUES ({}, 3, '{}', {}, {}, 1, {}, '{}', 2237, 2, 'flinpay', '{}');".format(
			payment_record_id, bank_account_number, bank_account_id, amount, bid_id, mobile, deduct_time
		).replace("'None',", "null,").replace("None,", "null,")

		cursor_sake.execute(insert_payment_record_sql)
		print(item['user_cid'] + ',' + item['phone'] + '，' + str(bid_id) + ', insert payment_record ok')


		ks_loan_order_tran_sql = "SELECT * FROM ks_loan_order_tran where partner_code='{}' and order_id={}".format(
			'mautunai', item['id'])
		cursor_rum.execute(ks_loan_order_tran_sql)
		ks_loan_order_tran_by_order_id_list = cursor_rum.fetchall()
		for tran in ks_loan_order_tran_by_order_id_list:
			if int(tran['current_status']) == 200 or int(tran['current_status']) == 132:
				bill_extension_id = snowflake.client.get_guid()
				bill_extension_status = convert_status(int(tran['current_status']))
				bill_extension_creat_time = tran['gmt_create']
				bill_extension_repayment_time = tran['repayment_time']
				if tran['expiry_time'] == None:
					bill_extension_overdue_days = 0
				else:
					bill_extension_overdue_days = cal_time(tran['expiry_time'][0, 11])
				insert_bill_extension_sql = "INSERT INTO `sake`.`bill_extension`(`id`,`gmt_create`, `gmt_modified`, `bid_id`, `user_id`, `product_id`, `saas_id`, `channel_id`, `status`, `repayment_corpus`, `repayment_amount`, `real_repayment_amount`, `real_repayment_corpus`, `overdue_amount`, `real_pay_overdue_fine`, `current_overdue_days`, `bank_account_number`, `contract_no`, `name`, `cid`, `mobile`, `overdue_day`, `repayment_time`, `is_reloan`) " \
						  "VALUES ({}, '{}', '{}', {}, {}, {}, 2237, 2, {}, {}, {}, {}, {}, {}, {}, {}, '{}', '{}', '{}', '{}', '{}', {}, '{}', {});".format(
					bill_extension_id, bill_extension_creat_time, bill_extension_creat_time, bid_id, new_user_id, product_id, bill_extension_status, repayment_corpus, repayment_amount,
					real_repayment_amount, real_repayment_corpus, overdue_manage_fee, overdue_manage_fee, bill_extension_overdue_days,
					bank_account_number, contract_no, name, cid, mobile, overdue_days, bill_extension_repayment_time, is_reloan
				).replace("'None',", "null,").replace("None,", "null,")
				cursor_sake.execute(insert_bill_extension_sql)
				print(item['user_cid'] + ',' + item['phone'] + '，' + str(bid_id) + ','+ str(bill_extension_status) + ', insert bill_extension ok')
	conn_sake.commit()


def insert_user(conn_sake, cursor_sake, new_item, bankcard_id):

	user_id = snowflake.client.get_guid()
	cid = new_item['user_cid']
	mobile = new_item['phone']
	name = new_item['user_name']

	registerChannel = new_item['channel_source']
	mobileMd5 = hashlib.new('md5', mobile.encode('gbk')).hexdigest()
	cidMd5 = hashlib.new('md5', cid.encode('gbk')).hexdigest()
	insert_user_sql = "INSERT INTO `sake`.`user`(`id`, `saas_id`, `cid`, `mobile`, `name`, `register_channel`, `register_channel_id`, `mobile_md5`, `cid_md5`) VALUES ({}, 2237, '{}', '{}', '{}', '{}', 2, '{}', '{}');".format(
		user_id, cid, mobile, name, registerChannel, mobileMd5, cidMd5).replace("'None',", "null,").replace("None,", "null,")
	cursor_sake.execute(insert_user_sql)
	print(new_item['user_cid'] + ',' + new_item['phone'] + ', insert user ok')

	user_detail_id = snowflake.client.get_guid()
	# if len(new_item['marital']) > 0:
	# 	marital_status = new_item['marital']
	# bank_account_id = convert_back_id(new_item['debit_open_bank_id'])

	bank_account_id = bankcard_id
	first_apply_time = new_item['submit_time']
	first_deduct_time = new_item['loan_time']
	loan_amount = new_item['actual_amount']
	name_mirror = name[-1::-1]
	liveness_score = new_item['face_score']

	thirdpart_response_data = request_method(new_item['thirdparty_order_id'])
	idcard_front_img = None
	live_img = None
	idcard_image_hand = None
	address = None
	gender = None
	birth_day = None
	marital_status = None
	month_income = None
	education = None
	emrg_contact_name_a = None
	emrg_contact_mobile_a = None
	emrg_contact_rel_a = None
	emrg_contact_name_b = None
	emrg_contact_mobile_b = None
	emrg_contact_rel_b = None
	work_type = None
	company_name = None
	has_work =None

	if thirdpart_response_data != None:
		idcard_front_img = get_upload_url(thirdpart_response_data['data']['idcard_image_front'], new_item['thirdparty_order_id'])
		live_img = get_upload_url(thirdpart_response_data['data']['face_img_url'], new_item['thirdparty_order_id'])
		idcard_image_hand = get_upload_url(thirdpart_response_data['data']['work_picture'], new_item['thirdparty_order_id'])
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
		contact = thirdpart_response_data['data']['contact']

	# insert_user_detail_sql = "INSERT INTO `sake`.`user_detail`(`id`, `saas_id`, `user_id`, `cid`, `mobile`, `name`, `channel_id`, `channel_name`, `bank_account_id`, `operator_id`, `first_apply_time`, `first_deduct_time`, `loan_amount`, `name_mirror`, `cid_md5`, `mobile_md5`, `liveness_score`, `idcard_front_img`, `live_img`, `idcard_image_hand`) " \
	# 						 "VALUES ({}, 2237, {}, '{}', '{}', '{}', 2, '{}', {}, 0, '{}', '{}', {}, '{}', '{}', '{}', {}, '{}', '{}', '{}');".format(
	# 	user_detail_id, user_id, cid, mobile, name, registerChannel, bank_account_id, first_apply_time, first_deduct_time,
	# 	loan_amount, name_mirror, cidMd5, mobileMd5, liveness_score, idcard_front_img, live_img, idcard_image_hand).replace("'None',", "null,").replace("None,", "null,")

	insert_user_detail_sql = "INSERT INTO `sake`.`user_detail`(`id`, `saas_id`, `user_id`, `cid`, `mobile`, `name`, `channel_id`, `channel_name`, `address`, `gender`, `birthday`, `marital_status`, `income`, `education_level`, `bank_account_id`, `operator_id`, `first_apply_time`, `first_deduct_time`, `loan_amount`, `emrg_contact_name_a`, `emrg_contact_name_b`, `emrg_contact_mobile_a`, `emrg_contact_mobile_b`, `emrg_contact_rel_a`, `emrg_contact_rel_b`, `idcard_front_img`, `live_img`, `name_mirror`, `cid_md5`, `mobile_md5`, `liveness_score`, `has_work`, `work_type`, `company_name`, `idcard_image_hand`) " \
	"VALUES ({}, 2237, {}, '{}', '{}', '{}', 2, '{}', '{}', {}, '{}', {}, {}, None, {}, 0, '{}', '{}', {}, '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', {}, {}, {}, '{}', '{}');".format(
		user_detail_id, user_id, cid, mobile, name, registerChannel, address, gender, birth_day, marital_status,
		month_income, bank_account_id, first_apply_time, first_deduct_time, loan_amount, emrg_contact_name_a,
		emrg_contact_name_b, emrg_contact_mobile_a, emrg_contact_mobile_b, emrg_contact_rel_a, emrg_contact_rel_b,
		idcard_front_img, live_img, name_mirror, cidMd5, mobileMd5, liveness_score, has_work, work_type, company_name, idcard_image_hand
	).replace("'None',", "null,").replace("None,", "null,")

	cursor_sake.execute(insert_user_detail_sql)

	print(new_item['user_cid'] + ',' + new_item['phone'] + ', insert user_detail ok')

	bank_id = convert_back_id(new_item['debit_open_bank_id'])
	debit_bank_name = new_item['debit_bank_name']
	bank_account_number = new_item['debit_bank_card']
	insert_bankcard_sql = "INSERT INTO `sake`.`bankcard`(`id`, `user_id`, `bank_id`, `bank_account_number`, `bank_account_name`, `bank_full_name`, `payment_channel`, `check_result`, `saas_id`, `bank_code`)" \
						  " VALUES ({},  {}, {}, '{}', '{}', '{}', 'flinpay', 0, 2237, '{}');".format(
		bankcard_id, cid, bank_id, bank_account_number, debit_bank_name, debit_bank_name, debit_bank_name
	)
	cursor_sake.execute(insert_bankcard_sql)
	conn_sake.commit()
	print(new_item['user_cid'] + ',' + new_item['phone'] + ', insert bankcard ok')
	return user_id, contact

def confirm_data(cursor_rum, cursor_sake, conn_sake, total, last_offset, page_size):
	last_time_sql = "SELECT * FROM ks_loan_order where status in('100','121','131','132','200') and  partner_code='{}' limit {},{}".format(
		'mautunai', last_offset, page_size)
	cursor_rum.execute(last_time_sql)
	source_list = cursor_rum.fetchall()
	# 多字段排序分组
	user_sort = sorted(source_list, key=lambda x: (x["user_cid"], x["phone"]))
	user_group = groupby(user_sort, key=lambda x: (x["user_cid"], x["phone"]))
	group_count = 0
	for key, group in user_group:
		sort_list = sorted(list(group), key=lambda x: (x["gmt_create"]))
		new_item = sort_list[-1]
		group_count = group_count + 1
		bankcard_id = snowflake.client.get_guid()
		# user & user_detail & bankcard, 返回user_id
		new_user_id, contact = insert_user(conn_sake, cursor_sake, new_item, bankcard_id)

		for item in sort_list:
			total = total + 1
			# bid & bill & bill_extension
			insert_bid(conn_sake, cursor_sake, item, new_user_id, bankcard_id, contact)

			print('第%s条迁移成功, 状态是%s' % (total, convert_status(int(item['status']))))
			print('---------------------------------------------------------------------------------------------------------------')
	print('偏移量为%s模块内，根据身份证和手机号总共有%s组' % (last_offset, group_count))
	return total

def public_sql(cursor_sake):
	loan_app_sql = "INSERT INTO `sake`.`loan_app`(`id`,`channel_id`, `channel_name`, `channel_label`, `saas_id`, `app_id`, `payment_channel`, `contract_url`, `channel_product_id`, `channel_product_name`) VALUES (9, 2, 'KCASH', 'KCASH', 2237, '202109286666', 'flinpay', NULL, 612, 'mautunai');"
	cursor_sake.execute(loan_app_sql)
	print('insert loan_app ok')
	org_manage_sql = "INSERT INTO `sake`.`org_manage`(`id`, `org_code`, `parent_code`, `org_name`, `org_profile`, `org_admin`, `gmt_create`, `gmt_modified`, `is_deleted`, `saas_id`) VALUES (20, '1000', NULL, '总部', 'all', 'all', '2021-09-29 10:19:51', '2021-09-29 10:19:51', 1, 2237);"
	cursor_sake.execute(org_manage_sql)
	print('insert org_manage ok')
	product_sql = "INSERT INTO `sake`.`product`(`id`, `gmt_create`, `gmt_modified`, `is_deleted`, `name`, `saas_id`, `cut_interest_rate`, `overdue_interest_rate`, `extend_repayment_rate`, `daily_interest_rate`, `annually_interest_rate`, `amount`, `period_day`, `manage_fee`, `overdue_manage_fee`, `bad_bid_deadline`, `cut_interest_fee`, `is_prepayment_enabled`, `is_enabled`, `description`, `repayment_type`, `message_service_fee_rate`, `account_manage_fee_rate`, `breach_account_fee_rate`, `interest_collect_style`, `max_loan_amount`, `composite_daily_rate`, `composite_overdue_daily_rate`, `manage_fee_style`, `collect_scale`, `is_auto`, `overdue_number`, `repeated_loan_scope_A`, `repeated_loan_scope_B`, `raise_amount_A`, `raise_amount_B`, `channel_id`, `channel_name`, `product_rule`, `is_extending`) VALUES (200, '2021-09-29 10:24:15', '2021-09-29 10:24:15', 0, 'default', 2237, 0.35, 0.0800, 0.35, 0.00, 0.00, 1400000.00, 7, 0.00, 0.00, 0, 0.0000, 1, 1, NULL, NULL, NULL, NULL, NULL, 0, 1500000.00, NULL, NULL, NULL, 0.3500, 0, NULL, NULL, NULL, NULL, NULL, -1, NULL, '{\"cutInterestRate\":35,\"amount\":1400000,\"overdueInterestRate\":8,\"maxLoanAmount\":1500000,\"isExtending\":1,\"periodDay\":7,\"extendRepaymentRate\":35}', 1);"
	cursor_sake.execute(product_sql)
	print('insert product ok')
	supervisor_sql = "INSERT INTO `sake`.`supervisor`(`id`, `account`, `reality_name`, `password`, `is_allow_login`, `mobile`, `is_deleted`, `channel_id`, `channel_name`, `saas_id`, `gender`, `org_manage_id`) VALUES (31, 'test612', 'test612', '2E52ABF010818B4D3EC217D8AFAF3D9F', 1, '123', 0, 0, '自然渠道', 2237, 0, '20');"
	cursor_sake.execute(supervisor_sql)
	print('insert supervisor ok')
	roles_of_supervisor_sql = "INSERT INTO `sake`.`roles_of_supervisor`(`supervisor_id`, `role_id`, `saas_id`, `is_deleted`) VALUES (31, 12, 2237, 0);"
	cursor_sake.execute(roles_of_supervisor_sql)
	print('insert roles_of_supervisor ok')
	role_sql = "INSERT INTO `sake`.`role`(`id`, `role_name`, `role_desc`, `saas_id`, `is_deleted`, `gmt_create`, `gmt_modified`, `menu_of_role_id`, `related_menu`, `checked_menu`, `is_allowed`, `is_urged`) VALUES (12, '管理员', '管理员', 2237, 0, '2021-09-29 09:00:35', '2021-09-29 09:00:58', NULL, '1,2,3,4,5,7,8,9,6,10,11,32,34,15,36,33,14,31,35,13,12,16,17,19,18,20,21,25,23,22,29,24,26,30,27,28', '1,2,3,4,5,7,8,9,6,10,11,32,34,15,36,33,14,31,35,13,12,16,17,19,18,20,21,25,23,22,29,24,26,30,27,28', 1, 0);"
	cursor_sake.execute(role_sql)
	print('insert role ok')

def execute(cursor_rum, cursor_sake, conn_sake):
	try:
		# public_sql(cursor_sake)
		pass
	except Exception as error:
		conn_sake.rollback()
		print('起始插入错误', error)
		return
	conn_sake.commit()
	print('---------------------------------------------------------------------------------------------------------------')

	total = 0
	sql = "SELECT count(1) FROM ks_loan_order where status in('100','121','131','132','200') and partner_code='{}'".format(
		'mautunai')
	cursor_rum.execute(sql)
	source_count = cursor_rum.fetchall()
	# 分块读取，避免一次性读取大量数据
	page_size = 5000
	times = math.floor(int(source_count[0]['count(1)']) / page_size)
	print('一共有数据有%s条' % int(source_count[0]['count(1)']))
	print('需要遍历，共有%s模块' % times)
	# last_count = int(source_count[0]['count(1)']) % page_size
	for i in range(0, times):
		offset = i * page_size
		print('--- 偏移量为%s ---' % offset)
		total = confirm_data(cursor_rum, cursor_sake, conn_sake, total, offset, page_size)
		print('--- 第%s模块，完成 ---' % (i + 1))
	last_offset = times * page_size
	print('--- 最后偏移量为%s ---' % last_offset)
	total = confirm_data(cursor_rum, cursor_sake, conn_sake, total, last_offset, 1)
	print('#--- 迁移完成, %s ---#' % total)

if __name__ == '__main__':
	# 开发环境
	conn_rum = pymysql.Connect(
		host='120.55.200.28',
		port=3306,
		user='ecreditpal', passwd='vaiFA3MQ9dLcDjWL',
		db='rum', charset='utf8',
		cursorclass=pymysql.cursors.DictCursor)
	cursor_rum = conn_rum.cursor()

	conn_sake = pymysql.Connect(
		host='120.55.200.28',
		port=3306,
		user='ecreditpal', passwd='vaiFA3MQ9dLcDjWL',
		db='sake', charset='utf8',
		cursorclass=pymysql.cursors.DictCursor)
	cursor_sake = conn_sake.cursor()

	execute(cursor_rum, cursor_sake, conn_sake)
	cursor_rum.close()
	conn_rum.close()
	cursor_sake.close()
	conn_sake.close()

	# 生产环境
	# with SSHTunnelForwarder(
	# 		("52.184.8.192", 3007),
	# 		ssh_username="lifeng.ye",
	# 		ssh_pkey="~/.ssh/baipeng.pem",
	# 		remote_bind_address=("rm-k1as78x4dp90382jt.mysql.ap-southeast-5.rds.aliyuncs.com", 3306),
	# 		local_bind_address=("0.0.0.0", 1022)
	# ) as tunnel:
	# 	conn_rum = pymysql.Connect(
	# 		host='127.0.0.1',
	# 		port=tunnel.local_bind_port,
	# 		user='tropic', passwd='5pdUNJBoBW#GZldg',
	# 		db='rum', charset='utf8',
	# 		cursorclass=pymysql.cursors.DictCursor)
	#
	# 	cursor_rum = conn_rum.cursor()
	#
	# 	conn_sake = pymysql.Connect(
	# 		host='127.0.0.1',  # 测试环境
	# 		port=tunnel.local_bind_port,
	# 		user='tropic', passwd='5pdUNJBoBW#GZldg',
	# 		db='sake', charset='utf8',
	# 		cursorclass=pymysql.cursors.DictCursor)
	# 	cursor_sake = conn_sake.cursor()
	#
	# 	if not cursor_rum:
	# 		raise (NameError, "连接数据库失败")
	#
	# 	execute(cursor_rum, cursor_sake, conn_sake)
	# 	cursor_rum.close()
	# 	conn_rum.close()
	# 	cursor_sake.close()
	# 	conn_sake.close()
