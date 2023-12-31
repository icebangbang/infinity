from datetime import datetime
from app.main.db.mongo import db
from app.main.utils import date_util, collection_util


def save_history_event():
    entities = []
    entity = dict(country="中国",
                  event=["金融委会议"],
                  keyword=["稳预期", "稳市场","恢复市场信心","对冲美联储加息","a股政策底"],
                  background=['股市连续大跌'],
                  desc="""
                  1.积极出台对市场有利的政策,慎重出台收缩性政策
                  2.对市场关注的热点问题要及时回应
                  3.凡是对资本市场产生重大影响的政策,应事先与金融部门协调,保持政策预期的稳定和一致性
                  4.宏观经济运行,切实振作一季度经济,货币政策要主动应对,新增贷款要保持适度增长
                  4.关于中概股,目前中美双方监管机构保持了良好沟通,已取得积极进展,正在致力于形成具体的合作方案.中国政府继续支持各类企业到境外上市
                  5.关于香港金融市场稳定问题,内地与香港两地监管机构要加强沟通合作""",
                  comment="""该消息午间放出,受此影响,下午a股和港股绝地反击,a股从最低3023点,最重收盘3170,收涨3.48%,终结连续的大跌.
                  a50指数出现8.9%的历史性涨幅.港股也在连续大跌之后,出现9%报复性反弹,跌的最狠的恒生指数,出现22%的报复性反弹.
                  该会议主要提振信心,阻止非理性恐慌性杀跌,对冲即将到来的美联储加息""",)
    entities.append(entity)
    entity = dict(country="美国",
                  event=["加息"],
                  keyword=["加息25基点", "2022首次加息"],
                  background=['美国3月CPI环比上涨1.2%，同比增长8.5%，同比涨幅创1981年12月以来最高水平'],
                  desc="""美联储如预期加息25个基点,上调联邦基金利率目标区间25个基点到0.25%至0.5%之间,点阵图显示年内还将加息六次""",
                  comment="""受此影响,美国债券市场价格出现暴跌,国债收益率出现暴涨,5年期国债收益率和10年期国债收益率十分接近,
                  如果2年期国债收益率超过10年期的,就会出现收益率倒挂,这是明显的美国经济衰退信号.
                  美联储加息的举动,主要还是为了压低通胀.如果通胀失控,或者恶意收割他国资本,那么美国的加息力度将会更大""",
                  date=datetime(2022, 3, 17))
    entities.append(entity)
    entity = dict(country="美国",
                  event=["加息"],
                  keyword=["加息50基点"],
                  desc="""当地时间5月4日下午，美联储通过会议决定将美国联邦基金利率增加0.5%（即上涨50个基点），以降低美国高企的通胀率。加息后，联邦基金利率区间增至0.75%到1%。
                  这也是美联储22年来首次一次升息0.5%。""",
                  comment="""据说市场预期是加息75个点,实际加息50个点,超出预期,所以当日美股大涨,但是次日又大跌.
                  实际上这是美联储预期管理的效果.""",
                  date=datetime(2022, 5, 5))
    entities.append(entity)

    entity = dict(country="美国",
                  event=["缩表"],
                  keyword=["9万亿美元资产负债表", "475亿美元","950亿美元"],
                  desc="""美联储还宣布将启动一项缩表计划，从6月开始，每月从9万亿美元资产负债表中减少475亿美元资产负债，三个月后，每月将减少950亿美元""",
                  comment="",
                  date=datetime(2022, 5, 5))
    entities.append(entity)


    history_event = db['history_event']
    history_event.drop()
    history_event.insert_many(entities)

def run_stock_feature_task():
    """
        定时轮询表,然后发布任务
        :return:
        """
    history_task = db["history_task"]
    history_task_detail = db["history_task_detail"]
    task_info = history_task.find_one({"is_finished": 0, "task_name": "个股历史特征按批次跑批"})

    if task_info is None:
        return

    minutes = date_util.get_minutes_between(datetime.now(), task_info['update_time'])

    if minutes <= -1:
        # 保持间隔,不需要跑的太猛
        return

    # 这里可能会有重复执行
    global_task_id = task_info['global_task_id']
    # 正序排序
    task_detail_list = list(history_task_detail.find({"global_task_id": global_task_id,
                                                      "status": {"$in": [0, 1]}}).sort("_id", 1))

    if collection_util.is_not_empty(task_detail_list):
        task_detail_item = task_detail_list[0]
        # 最近一个任务还在处理中,不做额外处理
        if task_detail_item['status'] == 1:
            return

        date = task_detail_item['date']
        index = task_detail_item['index']

        flow_job_info = task_info['task_info']
        flow_job_info['global_task_id'] = global_task_id + "_" + str(index)
        flow_job_info['callback_service'] = "app.main.task.history_task.update_history_feature"
        flow_job_info['params'] = dict(
            from_date_ts=date_util.to_timestamp(date),
            end_date_ts=date_util.to_timestamp(date),
            global_task_id=global_task_id
        )

        # stock_task.submit_stock_feature_by_job.apply_async(kwargs=flow_job_info)
    else:
        history_task.update_one({"_id": task_info["_id"]}, {"$set": {"is_finished": 1}})
        # task_dao.notify(task_info['task_info'])


if __name__ == "__main__":
    run_stock_feature_task()
