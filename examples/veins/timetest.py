import datetime
import time
from func_timeout import func_set_timeout, exceptions

class TEST:
    @func_set_timeout(3)
    def __init__(self, parameter):
        self.parameter = parameter
        time.sleep(4)
        print("初始化成功")

    def TEST_main(self):
        print("TEST_main函数运行成功")

if __name__ == "__main__":
    para = [100, 200]
    flag1 = 1
    try:
        run = TEST(para)
    except exceptions.FunctionTimedOut:
        print('执行函数超时')
        flag1 = 0
    if flag1 == 1:
        run.TEST_main()