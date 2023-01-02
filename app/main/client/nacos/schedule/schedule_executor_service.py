#!/user/bin/python3
# @Author:  LSY
# @Date:    2018/7/6

import time
import threading


def now():
    return int(time.time())


class Node(object):
    def __init__(self, data, next=None):
        self.data = data
        self.next = next


class Link(object):
    """docstring for Link"""

    def __init__(self):
        self.head = Node(None, None)


class Task(threading.Thread):

    def __init__(self, task_id, executor, timestamp, period):
        threading.Thread.__init__(self)
        self.task_id = task_id
        self.executor = executor
        self.timestamp = timestamp
        self.period = period

    def run(self):
        """
        """
        self.executor.callable()


execute_service_lock = threading.Lock()


class ExecuteService(threading.Thread):
    """docstring for ScheduleExecuteService"""

    def __init__(self):
        threading.Thread.__init__(self)
        self.link = Link()

    def run(self):
        while True:
            p = self.link.head
            while p.next and p.next.data.timestamp < now():
                p.next.data.start()
                if p.next.data.period > 0:
                    self.add(Task(p.next.data.task_id,
                                  p.next.data.executor,
                                  p.next.data.timestamp + p.next.data.period,
                                  p.next.data.period))

                execute_service_lock.acquire()
                p.next = p.next.next
                execute_service_lock.release()

            time.sleep(1)

    def add(self, task):
        """
          添加定时任务
        """
        execute_service_lock.acquire()
        p = self.link.head

        while p.next and p.next.data.timestamp < task.timestamp:
            p = p.next
        p.next = Node(task, p.next)

        execute_service_lock.release()

    def remove(self, task_id):
        """
          删除定时任务
        """
        execute_service_lock.acquire()
        p = self.link.head

        while p.next:
            if p.next.data.task_id == task_id:
                p.next = p.next.next
                continue
            p = p.next

        execute_service_lock.release()


class ScheduleService(object):

    def __init__(self):
        self.execute = ExecuteService()
        self.execute.setDaemon(True)
        self.execute.start()

    def schedule(self, task_id, executor, delay):
        """
        """
        self.execute.add(Task(task_id, executor, now() + delay, 0))

    def schedule_at_fixed_rate(self, task_id, executor, init_delay, period):
        """
        """
        self.execute.add(Task(task_id, executor, now() + init_delay, period))

    def drop_schedule(self, task_id):
        """
        """
        self.execute.remove(task_id)
