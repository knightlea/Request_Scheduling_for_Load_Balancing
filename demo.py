import csv
import random
import math
import copy
from time import *

N = ["BS0", "BS1", "BS2", "BS3", "BS4", "BS5", "BS6", "BS7", "BS8", "BS9", "BS10", "BS11"]  # 基站集合
M = ["M0", "M1", "M2", "M3", "M4", "M5"]  # 服务器集合  对应BS编号: 2 4 5 7 8 11
ServerInBS = [2, 4, 5, 7, 8, 11]  # BS中的服务器编号
Server_to_BS_dict = {}  # BS编号对应的数组号
Server_to_BS_dict[0] = 2
Server_to_BS_dict[1] = 4
Server_to_BS_dict[2] = 5
Server_to_BS_dict[3] = 7
Server_to_BS_dict[4] = 8
Server_to_BS_dict[5] = 11

distance = [[0, 1, 2, 3, 4, 1, 2, 3, 3, 4, 4, 5],
            [1, 0, 1, 2, 3, 1, 2, 3, 3, 4, 4, 4],
            [2, 1, 0, 1, 2, 2, 3, 2, 4, 4, 3, 3],
            [3, 2, 1, 0, 1, 3, 2, 1, 3, 3, 2, 2],
            [4, 3, 2, 1, 0, 4, 3, 2, 4, 3, 2, 1],
            [1, 1, 2, 3, 4, 0, 1, 2, 2, 3, 3, 4],
            [2, 2, 3, 2, 3, 1, 0, 1, 1, 2, 2, 3],
            [3, 3, 2, 1, 2, 2, 1, 0, 2, 2, 1, 2],
            [3, 3, 4, 3, 4, 2, 1, 2, 0, 1, 2, 3],
            [4, 4, 4, 3, 3, 3, 2, 2, 1, 0, 1, 2],
            [4, 4, 3, 2, 2, 3, 2, 1, 2, 1, 0, 1],
            [5, 4, 3, 2, 1, 4, 3, 2, 3, 2, 1, 0]
            ]  # 基站之间的跳数

S = [i for i in range(50)]  # 服务集合 50个服务 每个服务以编号代替名称
'''
svc_num:
0-13:   taobao.com
14-16:  taobaocdn.com
17-19:  aliyun.com
20:     aliyuncs.com
21-29:  alipay.com
30:     alipayobjects.com
31-45:  alicdn.com
46-48:  alibaba.com
49:     alisoft.com
'''
F = 20  # 服务器处理频率 10GHZ
fs = [0.5, 1.3, 0.1, 1.1, 1.6, 0.5, 0.1, 1.7, 0.3, 1.9,
      1.3, 1.6, 1.3, 1.0, 0.4, 0.9, 0.3, 1.7, 2.0, 1.4,
      1.3, 1.5, 0.4, 1.8, 0.7, 1.4, 1.6, 0.8, 0.2, 1.1,
      1.3, 1.1, 1.5, 1.4, 1.4, 1.0, 1.7, 1.3, 0.1, 1.6,
      1.5, 1.4, 1.4, 1.1, 0.9, 2.0, 1.7, 0.4, 1.5, 0.6]  # 每个服务所需要的处理频率 GHz

C = 200  # 服务器容量200GB
cs = [9, 8, 7, 7, 5, 6, 5, 5, 10, 10,
      8, 6, 9, 8, 10, 9, 9, 5, 8, 5,
      7, 9, 10, 5, 8, 9, 8, 5, 5, 8,
      6, 5, 10, 10, 9, 8, 5, 6, 9, 5,
      5, 10, 8, 10, 7, 8, 9, 6, 9, 5]  # 每个服务所需要的存储空间

Bandwidth_per_loc=[160 for i in range(12)]
Bandwidth_per_svc=[1.0, 0.4, 1.0, 0.5, 0.7, 0.2, 0.3, 0.8, 0.8, 0.8, 0.2, 0.7, 0.6, 0.5, 0.4, 0.7, 0.9, 0.3, 0.7, 0.5, 0.2, 0.7, 0.4, 0.9, 1.0, 0.1, 0.8, 1.0, 0.5, 0.7, 0.5, 0.9, 0.7, 0.7, 0.1, 0.2, 0.4, 0.5, 0.1, 0.2, 1.0, 0.8, 0.9, 0.4, 0.6, 0.2, 0.5, 0.8, 0.1, 0.9]


A = list()  # 服务器缓存服务情况，以12个小时为一个时隙单位，12小时内服务器缓存不会变化 list()=A[t][server_num]: 该时隙下某server的服务缓存情况 62*6数组 服务保存在一个list里
for i in range(63):
    tmp = list()  # []
    for j in range(6):
        tmp2 = list()
        tmp.append(tmp2)  # [[]]
    A.append(tmp)  # [[[],[]],[[],[]]]

B = list()  # 统计一段时间内的服务器缓存服务被用户访问情况 B[t][server_num]=dict
for i in range(63):
    tmp = list()
    for j in range(6):
        tmp2 = {}
        tmp.append(tmp2)
    B.append(tmp)


D = []  # 统计一段时间内服务器的总访问量 D[slot][server_num]
for i in range(63):
    tmp = []
    for j in range(6):
        tmp2 = 0
        tmp.append(tmp2)
    D.append(tmp)

E = []
for i in range(63):
    tmp = []
    for j in range(50):
        tmp2 = 0
        tmp.append(tmp2)
    E.append(tmp)

request_by_time = list()
filename="file_location/request_information_city_name.csv"
with open(filename, 'r', encoding='UTF-8') as f:
    reader = csv.reader(f)
    for i in reader:
        tmp = list()
        tmp.append(i[0])
        tmp.append(i[1])
        tmp.append(i[2])
        tmp.append(i[3])
        tmp.append(i[4])
        tmp.append(i[5])
        tmp.append(i[6])
        tmp.append(i[7])
        tmp.append(i[8])
        request_by_time.append(tmp)

'''
request各字段含义:
0: BS_id
1: start_time
2: end_time
3: instance_num
4: service_num
5: job_name
6: machine_id
7: cpu_num
8: mem_num
'''

server = list(list(list()))
server0 = list(list())
server1 = list(list())
server2 = list(list())
server3 = list(list())
server4 = list(list())
server5 = list(list())
server.append(server0)
server.append(server1)
server.append(server2)
server.append(server3)
server.append(server4)
server.append(server5)

filename = "file_location/machine0.csv"
with open(filename, 'r', encoding='UTF-8') as f:
    reader = csv.reader(f)
    for i in reader:
        server0.append(i)

filename = "file_location/machine1.csv"
with open(filename, 'r', encoding='UTF-8') as f:
    reader = csv.reader(f)
    for i in reader:
        server1.append(i)

filename = "file_location/machine2.csv"
with open(filename, 'r', encoding='UTF-8') as f:
    reader = csv.reader(f)
    for i in reader:
        server2.append(i)

filename = "file_location/machine3.csv"
with open(filename, 'r', encoding='UTF-8') as f:
    reader = csv.reader(f)
    for i in reader:
        server3.append(i)

filename = "file_location/machine4.csv"
with open(filename, 'r', encoding='UTF-8') as f:
    reader = csv.reader(f)
    for i in reader:
        server4.append(i)

filename = "file_location/machine5.csv"
with open(filename, 'r', encoding='UTF-8') as f:
    reader = csv.reader(f)
    for i in reader:
        server5.append(i)
'''
服务器字段:
0: time_stamp
1: cpu_util_percent
2: mem_util_percent
'''


def Random_com():  # 通信时延
    # tmp = random.randint(43, 53)
    # tmp1 = 100.0
    # return tmp / tmp1
    return 0.5


def Comm_time(bs, server):  # 需要server的BS序号    BS_to_Server[server_num]=bs_num
    return Random_com() * distance[bs][server] * 2


def Server_f(time, server_num):
    rest_f = F * (100 - float(server[server_num][time][1])) / 100  # CPU剩余可用的频率
    return rest_f


def Handle_time(time, server_num, service_num):  # 需要server的num             #!!!在此添加限定条件
    rest_f = F * (100 - float(server[server_num][time][1])) / 100  # CPU剩余可用的频率
    return fs[service_num] / rest_f * 1000  # 单位 ms


def Time_all(queue_t, comm_t, handle_t):  # ServerInBS=[2,4,5,7,8,11]  0 1 2 3 4 5
    total_t = list(list())  # [server_num,total_time]
    for i in range(6):  # Server_num
        # num=Server_to_BS_dict[i] #对应BS的序号
        if handle_t[i] != 0:
            tmp = list()
            tmp.append(i)  # 服务器编号
            total = queue_t[i] + comm_t[i] + handle_t[i]
            tmp.append(total)  # 总处理时间
            tmp.append(handle_t[i])  # 存储排队时间
            total_t.append(tmp)
    # print("total_time_list: ")
    # print(total_t)

    res = sorted(total_t, key=(lambda x: [x[1], x[0]]))
    return res[0]  # server_num total_time queue_time


def Initial_queuing_time():  # 初始化每个服务器的等待时间队列，每个时隙下都有一个
    queuing_time = list()
    for i in range(6):  # Server序号
        queuing_time.append(0)
    return queuing_time


def Judge_mem(t, server_num, request_num):  # 服务器内存限制 判断是否分配
    request_mem = float(request_by_time[request_num][8])
    sum = float(server[server_num][t][2]) + request_mem
    if sum < 98:
        return True
    else:
        return False

def Judge_bandwidth(bandwidth_list, server_num, request_num):  # 无线带宽限制
    svc_id = int(request_by_time[request_num][4])
    sum_bandwidth=bandwidth_list[server_num]-Bandwidth_per_svc[svc_id]
    if sum_bandwidth > 0:
        # server[server_num][t][2] = str(sum)  # !!!直接修改读取的数组可能会对数据造成问题
        return True
    else:
        return False


def Add_mem(t, server_num, request_num):
    request_mem = float(request_by_time[request_num][8])
    sum = float(server[server_num][t][2]) + request_mem
    server[server_num][t][2] = str(sum)


def Request_time_to_server_time(request_time):  # 转换为服务器对应时隙
    a = request_time / 3600 / 12
    return math.floor(a)


def Judge_service_exit(t, server_num, service_num):  # 该时隙下服务器上是否存在该服务
    t_server = Request_time_to_server_time(t)
    if service_num in A[t_server][server_num]:
        return True
    else:
        return False


def Initial_service_on_server():  # 初始化服务器集群在第一个时隙下的服务缓存
    service_all = set()  # 全局服务缓存情况
    flag = False
    for i in range(6):  # 同一个服务器上缓存的服务不能重复
        service_singe = list()

        if len(service_all) < 50:
            flag = False
        else:
            flag = True  # 如果50个服务均已经缓存

        count = 0  # 内存容量
        while count <= 190:
            tmp = random.randint(0, 49)
            if flag == False:  # 查看是否50个服务均缓存 若均缓存则随便缓存其他服务 若没有缓存完全则缓存剩余的服务
                if tmp not in service_all:  # 和全局情况比较 此处缓存一定保证服务不会重复    首先缓存满50个服务
                    A[0][i].append(tmp)
                    service_all.add(tmp)
                    if len(service_all) == 50:
                        flag = True
                    service_singe.append(tmp)
                    count = count + cs[tmp]
            else:
                if tmp not in service_singe:  # 单个服务器内部缓存服务不能重复
                    A[0][i].append(tmp)
                    service_singe.append(tmp)
                    count = count + cs[tmp]

    for i in range(6):
        for j in A[0][i]:
            if j not in B[0][i].keys():
                B[0][i][j] = 0  # 0时隙(server_time)下对其缓存服务的访问量


def Check_all_service_exist(t):  # 确保在时隙内服务器集群有缓存所有服务

    exist = list()
    for i in range(6):
        for j in A[t][i]:  # list()
            exist.append(j)

    for i in range(50):
        if i not in exist:
            return False

    return True


glo_service_005=[]
glo_service_01=[]
glo_service_02=[]
glo_service_03=[]
glo_service_04=[]

sin_service_005=[]
sin_service_01=[]
sin_service_02=[]
sin_service_03=[]

def Change_service(timestamp):  # 62个时间段 每个时间段改变一次服务缓存情况
    t = Request_time_to_server_time(timestamp)

    service_pool = []  # 访问量少的所有服务的集合
    mem = [0] * 6
    if A[t][0] != []:  # 判断该时隙下是否到了应该改变服务的时候
        return
    else:
        total_visit_all = 0  # 总访问量
        single_service_visit = []
        for i in range(50):
            single_service_visit.append(0)

        for i in range(6):  ###对每个服务器按照上个时隙的访问请求比例进行缓存
            for j in B[t - 1][i].keys():  # server_i缓存的服务  !!!注意时间是上个时隙的时间
                total_visit_all += B[t - 1][i][j]
                single_service_visit[j] += B[t - 1][i][j]

        ratio = []
        service_list = []
        # service_lack=[] #未被访问的服务  一样需要被缓存

        for i in range(50):
            if total_visit_all > 0:
                # 调整访问概率
                if float(single_service_visit[i]) / float(total_visit_all) >= 0.3:
                    tmp = []
                    service_list.append(i)
                    tmp.append(i)  ###service_id
                    tmp.append(float(i) / float(total_visit_all))  ###访问占比
                    ratio.append(tmp)



        for i in range(6):              ###缓存上个时隙有访问的的所有服务
            for j in service_list:
                if j not in A[t][i] and mem[i]+cs[j]<=200:
                    A[t][i].append(j)
                    mem[i]+=cs[j]

        for i in range(6):
            total_visit = 0  # server_i该时段内的总访问量
            service_visit = []  #[[service_num,service_num_visit]...]   缓存服务列表
            for j in B[t - 1][i].keys():  # server_i缓存的服务  !!!注意时间是上个时隙的时间
                total_visit += B[t - 1][i][j]   #服务器i的总访问量
                tmp = []
                tmp.append(j)  # service_num
                tmp.append(B[t - 1][i][j])  # service_num_visit     有为0的情况
                service_visit.append(tmp)

            if total_visit > 0:
                for sv in service_visit:
                    p = float(sv[1]) / float(total_visit)  # 访问量占比
                    if p >= 0.2:
                        if sv[0] not in A[t][i] and mem[i]+cs[sv[0]]<=200:
                            A[t][i].append(sv[0])
                            mem[i] += cs[sv[0]]  # 外存大小


        service_have=[]
        for server_num in range(6):
            for service_num in A[t][server_num]:
                if service_num not in service_have:
                    service_have.append(service_num)

        service_pool=[]
        for service_num in range(50):
            if service_num not in service_have:
                service_pool.append(service_num)

        c = 0
        while c < len(service_pool):
            svce = service_pool[c]
            sver = random.randint(0, 5)  # server_num
            if svce not in A[t][sver] and mem[sver] + cs[svce] <= 200:
                A[t][sver].append(svce)
                mem[sver] += cs[svce]
                c += 1

        for i in range(6):  # 把能缓存的服务缓存满
            while mem[i] <= 190:
                r = random.randint(0, 49)
                if r not in A[t][i]:
                    A[t][i].append(r)
                    mem[i] = mem[i] + cs[r]

        for i in range(6):
            for j in A[t][i]:
                if j not in B[t][i].keys():
                    B[t][i][j] = 0  # 0时隙(server_time)下对其缓存服务的访问量



request_num = len(request_by_time)


X = list()  # 服务缓存情况 X[service_num][server_num] 50*6
for i in range(50):
    tmp = list()
    for j in range(6):
        tmp.append(0)
    X.append(tmp)


def Add_mem_Y(t, Y, requst_list):  # 以Y矩阵的形式添加内存
    for i in range(len(Y)):
        server_num = -1
        for j in range(6):
            if Y[i][j] == 1:
                server_num = j
                break
        Add_mem(t, server_num, requst_list[i][0])


def Release_mem(t, request_list, YY):
    for num in range(len(request_list)):
        server_n = -1
        for i in range(6):
            if YY[num][i] == 1:
                server_n = 1
                break
        f = float(server[server_n][t][2])
        f -= float(request_by_time[request_list[num][0]][8])
        server[server_n][t][2] = str(f)



def SA_heuristic(t, XX, res, request_list, sqn):  # 启发式分配请求算法   确保每个res的一行只有一个数为1

    for i in range(len(res)):  # 对每个请求进行分配
        con = 0

        for j in range(6):
            con = con + res[i][j]

        if con == 1:  # 只有一台服务器能处理该请求
            #cc1 += 1

            for j in range(6):
                if res[i][j] == 1:
                    sqn[j] += 1
                    break

            continue
        elif con == 0:  # 没有服务器能处理该请求
            #cc2 += 1

            choice = []  # 可以处理该请求的服务器
            for k in range(6):
                if XX[i][k] == 1:
                    tmp = []
                    tmp.append(k)
                    tmp.append(sqn[k])
                    tmp.append(-Server_f(t, k))
                    choice.append(tmp)

            result = sorted(choice, key=(lambda x: [x[1], x[2]]))

            choice_2 = []
            if len(result) == 1:
                r = result[0][0]
            else:
                choice_2.append(result[0][0])
                for j in range(1, len(result)):
                    if abs(result[j][1] - result[0][1]) <= 4 and result[j][2] < result[0][2]:
                        choice_2.append(result[j][0])

                ran = random.randint(0, len(choice_2) - 1)
                r = choice_2[ran]
            #r = result[0][0]

            sqn[r] += 1
            res[i][r] = 1

        else:  # 多个服务器可以处理该请求
            #cc3 += 1

            # way5 总是选择处理请求最少的服务器进行处理
            choice = []
            for j in range(6):
                if res[i][j] == 1:
                    tmp = []
                    tmp.append(j)
                    tmp.append(sqn[j])
                    tmp.append(-Server_f(t, j))
                    choice.append(tmp)
                    res[i][j] = 0

            result = sorted(choice, key=(lambda x: [x[1], x[2]]))

            choice_2 = []
            if len(result) == 1:
                r = result[0][0]
            else:
                choice_2.append(result[0][0])
                for j in range(1, len(result)):
                    if abs(result[j][1] - result[0][1]) <= 4 and result[j][2] < result[0][2]:
                        choice_2.append(result[j][0])

                ran = random.randint(0, len(choice_2) - 1)
                r = choice_2[ran]
            #r = result[0][0]

            sqn[r] += 1
            res[i][r] = 1


    return res


def SA_add(Y1, Y2, XX, t, request_list, sqn):  # 均为request_num*6阶矩阵

    res = list()
    for i in range(len(Y1)):
        tmp = list()
        for j in range(6):
            if Y1[i][j] == Y2[i][j]:
                tmp.append(0)  # 1 1为0     0 0为0
            else:
                tmp.append(1)  # 1 0为1     0 1为1
        res.append(tmp)

    for i in range(len(Y1)):
        for j in range(6):
            if XX[i][j] == 0:
                res[i][j] = 0  # 通过X判断该位的改变是否可取 !!!可能出现全0情况

    return SA_heuristic(t, XX, res, request_list, sqn)


def SA_des(Y1, Y2, XX, t, request_list, sqn):
    res = list()
    for i in range(len(Y1)):
        tmp = list()
        for j in range(6):
            if Y1[i][j] == Y2[i][j]:
                tmp.append(1)  # 1 1为1      0 0为1
            else:
                tmp.append(0)  # 0 1为0      1 0为0
        res.append(tmp)

    for i in range(len(Y1)):
        for j in range(6):
            if XX[i][j] != 1:  # X对应位为1不变 若不为1则变为0
                res[i][j] = 0

    return SA_heuristic(t, XX, res, request_list, sqn)


def SA_disturbance(t, Y, XX, request_list, sqn):  # 随机扰动

    Y_random = []  # 随机生成变换方向 V
    for y in range(len(Y)):
        tmp = list()
        for x in range(6):
            if random.random() > 0.5:
                tmp.append(1)
            else:
                tmp.append(0)
        Y_random.append(tmp)

    if random.random() < 0.5:
        return SA_add(Y, Y_random, XX, t, request_list, sqn)
    else:
        return SA_des(Y, Y_random, XX, t, request_list, sqn)


def SA_handle(t, Y, request_list):  # 针对有多个服务器处理的请求才调用该函数        !!!在此处可改为时间片轮转算法

    handle_list = []  # handle_list[server_num]=[[request1_num,service_num],[request2_num,service_num],...]
    total_time = []  # total_time[server_num]=[10,20,30,...]
    sum_t = 0  # 所有请求处理时间之和
    for i in range(6):  # 6台服务器
        handle_list.append([])
        total_time.append([])  # 每个服务器对应的request处理时间序列 total_time[server_num]=[10,20,30...]

    for i in range(len(Y)):  # 将请求分给服务器
        tmp = []
        tmp.append(request_list[i][0])  # 请求编号
        tmp.append(request_list[i][1])  # 服务编号
        server_n = -1
        for j in range(6):
            if Y[i][j] == 1:
                server_n = j  # 处理的服务器编号
                break
        handle_list[server_n].append(tmp)  # 该请求由服务器n处理

    queue_time = [0] * 6  # 每个服务器的等待时间

    for i in range(6):  # 计算每个服务器的请求处理时间
        if len(handle_list[i]) > 0:  # 如果服务器该时刻处理请求不为0
            r = sorted(handle_list[i], key=(lambda x: [fs[x[1]], x[0]]))  # 按频率排序 短任务优先

            for j in r:
                comm_t = Comm_time(int(request_by_time[j[0]][0]), i)

                handle_t = Handle_time(t, i, j[1])

                total_time[i].append(handle_t + comm_t + queue_time[i])

                sum_t += handle_t + comm_t + queue_time[i]

                queue_time[i] += handle_t  # 排队时间只包括处理时间

    sum_t = round(sum_t, 2)

    flag = True
    for i in range(6):
        for j in range(len(total_time[i])):
            if total_time[i][j]>3000:
                flag=False
    return sum_t,queue_time,flag


def SA_Judge(deltaE, T):
    if deltaE < 0:
        return 1
    else:
        p = math.exp(-deltaE / T)
        if p > random.random():
            return 1
        else:
            return 0


def Add_B(t, Y, request_list):
    tt = Request_time_to_server_time(t)
    for i in range(len(request_list)):
        server_num = -1
        for j in range(6):
            if Y[i][j] == 1:
                server_num = j
                break
        B[tt][server_num][request_list[i][1]] += 1



begin_time = time()
XX = []
# 退火算法参数
alpha = 0.96
Y_list_by_second = []  # 长度为有请求的时隙数
value_min_by_second = []
request_handle_seq_by_second = []

i = 0
Initial_service_on_server()  # 初始化0时刻服务缓存情况

record = []  # 记录每个时隙下有多少个请求
res_10 = []
res_20 = []
res_30 = []
record_10=[]
record_20=[]
record_30=[]
queue_by_all_time=[]

while i < request_num:
    rec = 0
    t = int(request_by_time[i][1])  # 该请求的start time
    tt = Request_time_to_server_time(t)  # 转换为服务器更新服务的时隙 12h


    Change_service(t)  # 判断是否应该改变缓存服务

    request_list = list()  # 当前时隙下的请求队列 request_num,ser_num
    p = i

    T_max = 5000
    T_min = 1
    Y_min = []
    value_min = 0

    while int(request_by_time[p][1]) == t:  # 统计改时隙下的请求队列
        rec += 1
        tmp = list()
        ser_num = int(request_by_time[p][4])
        tmp.append(p)  # 请求编号
        tmp.append(ser_num)  # 服务编号
        request_list.append(tmp)

        E[tt][ser_num] += 1
        p = p + 1
        if p < request_num:
            continue
        else:
            break
    # 得到了同一个时隙下的请求队列

    bandwidth_now=copy.deepcopy(Bandwidth_per_loc)

    for ii in range(50):
        for jj in range(6):
            X[ii][jj] = 0

    for ii in range(50):
        for jj in range(6):
            if ii in A[tt][jj]:
                X[ii][jj] = 1  # 缓存服务矩阵 50*6

    # queue_t=[0]*6
    if len(request_list) == 1:  # 当前时隙下只有一个请求，直接分配,贪心算法
        # print("request_list==1")
        # request_handle(t,request_list,queue_list)
        service_n = request_list[0][1]
        time_all = []
        for s in range(6):

            if X[service_n][s] == 1 and Judge_mem(t, s, request_list[0][0]) and Judge_bandwidth(bandwidth_now, s, request_num):
                bs_num = int(request_by_time[request_list[0][0]][0])
                tmpp = []
                tmpp.append(s)  # 服务器编号
                tmpp.append(Comm_time(bs_num, s) + Handle_time(t, s, service_n))  # 处理时间 单个请求不包含排队时延
                time_all.append(tmpp)
        rr = sorted(time_all, key=(lambda x: [x[1], x[0]]))
        server_n = rr[0][0]

        Add_mem(t, server_n, request_list[0][0])  # 给已经分配好的服务器添加内存

        Y = []
        for n in range(6):
            if n == server_n:
                Y.append(1)
            else:
                Y.append(0)
        value = rr[0][1]

        Y_min.append(Y)

        value = round(value, 2)

        Y_list_by_second.append(Y_min)
        value_min_by_second.append(value)
        request_handle_seq_by_second.append(request_list[0][0])
        Add_B(t, Y_min, request_list)

    else:  # 当前时隙有多个请求

        server_request_num = [0] * 6  # 每个时隙下 六台服务器处理的请求数量

        server_single_num = [0] * 6
        Y = []  # 请求处理矩阵 第i条请求给第j个服务器处理 request_num*6

        request_single = []  # 只有一台服务器能够处理的request
        request_mul = []  # 有多台服务器能够处理的request

        for re in request_list:  # 按照请求顺序存储服务器处理序列
            ser_num = re[1]  # 服务编号
            c = 0  # 统计有多少服务器可以处理该服务 若为1则写死
            server_l = []
            for sv_num in range(6):
                if X[ser_num][sv_num] == 1 and Judge_mem(t, sv_num, re[0]) and Judge_bandwidth(bandwidth_now, sv_num, re[0]):
                    c = c + 1
                    server_l.append(sv_num)
            if c == 1:  # 如果只有一台服务器能够处理
                tmpp = []
                for sr_num in range(6):
                    if sr_num == server_l[0]:
                        tmpp.append(1)
                    else:
                        tmpp.append(0)
                server_single_num[server_l[0]] += 1
                server_request_num[server_l[0]] += 1
                Y.append(tmpp)  # 首先存储只有单台能处理的情况 处理矩阵

                request_single.append(re)  # 添加到新序列中
            else:
                request_mul.append(re)


        queue_t = []
        if len(request_list) == len(request_single):  # 请求全部分配完毕 直接计算

            Add_mem_Y(t, Y, request_single)
            Y_min = Y
            value_min,queue_t,f = SA_handle(t, Y, request_single)
        else:  # 迭代分配

            YY = []  # 初始值 请求处理集合 多台服务器能处理的

            for y in range(len(request_mul)):
                Y_t = [0] * 6
                Y_r = random.randint(0, 5)
                while X[request_mul[y][1]][Y_r] != 1:  # 不能处理       #后续改进
                    Y_r = random.randint(0, 5)  # 随机生成处理序列 保证了每行之和为1
                Y_t[Y_r] = 1
                server_request_num[Y_r] += 1  # 初始值
                YY.append(Y_t)


            old_YY = copy.deepcopy(YY)  # 用于迭代的矩阵
            new_YY = copy.deepcopy(YY)

            if len(Y) > 0:  # 如果存在已经被处理的请求
                old_Y = copy.deepcopy(Y)  # 用于计算的矩阵
                new_Y = copy.deepcopy(Y)
            else:
                old_Y = []
                new_Y = []

            for y in old_YY:
                old_Y.append(y)  # 处理序列添加到原处理矩阵后面     YY合并到Y后面
                new_Y.append(y)

            for req in request_mul:
                request_single.append(req)  # 请求合并


            counter = 0
            value_old,q,f = SA_handle(t, old_Y, request_single)  # 计算总时间
            value_new = 0

            value_min = value_old
            Y_min = old_Y


            XX = []  # request_list_len *6
            for i in request_mul:  # request_id,service_num
                tmp = []
                for j in range(6):
                    if X[i[1]][j] == 1 and Judge_mem(t, j, i[0]) and Judge_bandwidth(bandwidth_now,j,i[0]):  # 内存限制
                        tmp.append(1)  # 服务是否在服务器上
                    else:
                        tmp.append(0)
                XX.append(tmp)

            while counter < 20 and T_max > T_min:  # 改进模拟退火算法
                sqn = copy.deepcopy(server_single_num)

                new_Y = copy.deepcopy(Y)

                new_YY = SA_disturbance(t, old_YY, XX, request_mul, sqn)  # 生成处理矩阵 均为多台服务器能处理的请求

                for y in new_YY:  # 拼接计算
                    new_Y.append(y)

                value_tmp,q,f = SA_handle(t, new_Y, request_single)  # 目标函数

                if f==False:
                    continue

                value_new=value_tmp

                delta = value_new - value_old  # 倾向于<0


                if SA_Judge(delta, T_max) == 1:  # 接受新的变化方向
                    value_old = value_new
                    old_YY = new_YY

                    if value_new < value_min:
                        value_min = value_new
                        Y_min = new_Y
                        server_request_num = sqn

                if delta < 0:
                    T_max = T_max * alpha
                #else:
                counter += 1


            Add_mem_Y(t, Y_min, request_single)

        queue_by_all_time.append(queue_t)

        Y_list_by_second.append(Y_min)
        value_min_by_second.append(value_min)

        if len(request_list) >= 30:
            res_30.append(value_min)
            record_30.append(len(request_list))

        if len(request_list) >= 20 and len(request_list) < 30:
            res_20.append(value_min)
            record_20.append(len(request_list))

        if len(request_list) >= 10 and len(request_list) < 20:
            res_10.append(value_min)
            record_10.append(len(request_list))


        request_seqence = []  # request_id 对应处理矩阵Y
        for re in request_single:
            request_seqence.append(re[0])
        request_handle_seq_by_second.append(request_seqence)

        Add_B(t, Y_min, request_single)
    i = p
    record.append(rec)







# cou=0
# for a in A:
#     if a!=[[], [], [], [], [], []]:
#         cou+=1
#
# print(cou)

