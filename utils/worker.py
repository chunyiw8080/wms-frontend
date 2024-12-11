from queue import Queue
import threading
from functools import wraps


class Worker:
    @staticmethod
    def run_in_thread_with_result(func):
        """装饰器：在单独线程中运行函数并返回结果"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            result_queue = Queue()

            def thread_function():
                try:
                    result = func(*args, **kwargs)
                    result_queue.put(result)  # 将结果放入队列
                except Exception as e:
                    result_queue.put(e)  # 将异常放入队列

            thread = threading.Thread(target=thread_function)
            thread.start()

            return thread, result_queue  # 返回线程和队列

        return wrapper

    @staticmethod
    def unpack_thread_queue(func, *args, **kwargs):
        """
        解封装线程与队列元组
        :param func: 请求函数
        :param args: URL
        :param kwargs: 携带的数据
        :return: 后端返回结果
        """
        thread, res_que = func(*args, **kwargs)
        thread.join()
        response = res_que.get()

        if isinstance(response, Exception):
            raise response
        if isinstance(response, tuple) and len(response) == 1:
            response = response[0]

        return response


