import csv
from itertools import groupby
import shutil
import pandas as pd

if __name__ == '__main__':
	user_detail_count = 0

	with open('user_detail.csv', 'r') as userFile:
		reader = csv.DictReader(userFile)
		user_group = groupby(reader, key=lambda x: (x["user_cid"], x["phone"]))
		# user_group = groupby(reader, key=lambda x: (x["user_cid"]))
		for key, group in user_group:
			user_detail_count = user_detail_count + 1
			user_list = list(group)
			# if len(user_list) > 1:
				# print('%s,%s' % (key[0],key[1]))
				# print('%s,%s' % (key[0], key[1]))
	userFile.close()


	bid_count = 0
	with open('bid.csv', 'r') as bidFile:
		reader = csv.DictReader(bidFile)
		bid_group = groupby(reader, key=lambda x: (x["thirdparty_order_id"]))
		for key, group in bid_group:
			bid_count = bid_count + 1
			if len(list(group)) > 1:
				print(key)
	bidFile.close()
	print('user_detail_count = %s, bid_count = %s' % (user_detail_count, bid_count))