#蚁群算法的基本原理:
#1、蚂蚁在路径上释放信息素
#2、碰到还没走过的路口，就随机挑选一条路走。同时，释放与路径长度有关的信息素
#3、信息素浓度与路径长度成反比。后来的蚂蚁再次碰到该路口时，就选择信息素浓度较高路径
#4、最优路径上的信息素浓度越来越大
#5、最终蚁群找到最优寻食路径

#蚁群算法计算过程如下：
#（1）初始化
#（2）为每只蚂蚁选择下一个节点
#（3）更新信息素矩阵
#（4）检查终止条件
#           -如果达到最大迭代数MAX_GEN，算法终止，转到第（5）步；
#           -否则，重新初始化所有的蚂蚁的Delt矩阵：
#           -所有元素初始化为0，Tabu表清空，Allowed表中加入所有的城市节点；
#           -随机选择它们的起始位置（也可以人工指定）。在Tabu中加入起始节点，Allowed中去掉该起始节点，重复执行2，3，4步；
#（5）输出最优值

import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as pli

#ALPHA：信息启发因子，影响蚂蚁选择下一节点的概率
#BETA：Beta值越大，蚁群越就容易选择局部较短路径，这时算法收敛速度会加快，但是随机性不高，容易得到局部的相对最优.
#Q：信息素常数
#RHO：信息素挥发因子，决定信息素挥发的速度
(ALPHA, BETA, RHO, Q) = (1.0,1.0,0.5,80.0)
#设置最大迭代次数为400
MAX_GEN = 400
#设定一共34个省会城市，直辖市和特别行政区，50只蚂蚁
(city_num, ant_num) = (34,50)

#34个省会城市的坐标
distance_x = [1032,1016,1722,1832,1840,1984,2292,2136,1981,1993,
              1713,2081,2420,2391,2465,2575,2813,2835,2967,2641,
              2413,2737,2907,2601,2350,2455,2560,2600,2921,3000,
              3051,2225,2486,2443]
distance_y = [662,1729,1309,1763,1359,1187,1017,1500,1854,2067,
              2169,2351,2322,1947,1769,1905,2077,1771,2139,1661,
              1467,1645,1687,1307,1235,1217,1070,1123,893,729,
              579,2556,2380,2388]
#两个10x10的矩阵，分别储存第i个城市到第j个城市的信息素和距离
pheromone_graph = [ [1.0 for col in range(city_num)] for raw in range(city_num)]
distance_graph = [ [0.0 for col in range(city_num)] for raw in range(city_num)]

#计算各个城市间的距离√((x1-x2)^2+(y1-y2)^2)
for i in range(city_num):
     for j in range(city_num):
         temp_distance = pow((distance_x[i] - distance_x[j]), 2) + pow((distance_y[i] - distance_y[j]), 2)
         temp_distance = pow(temp_distance, 0.5)
         distance_graph[i][j] =float(int(temp_distance + 0.5))


class Ant(object):
#初始化属性
    def __init__(self,ID):
        self.ID = ID
        self.clean_data()

#蚂蚁初始数据
    def clean_data(self):
        self.path = []                              # 当前蚂蚁的路径           
        self.total_distance = 0.0            # 当前路径的总距离
        self.move_count = 0                 # 移动次数
        self.current_city = -1                # 当前停留的城市
        self.can_visit_city = [True for i in range(city_num)]    # 探索城市的状态，全部置为True（即为可访问）
        city_index = random.randint(0,city_num-1)    # 随机选择初始出生点
        self.current_city = city_index          #将当前停留的城市置为出生点
        self.path.append(city_index)          #探索路径列表加入出生点
        self.can_visit_city[city_index] = False            #将出生点置为不可访问
        self.move_count = 1             #完成第一次移动（指出生）

#蚂蚁选择下一个城市
    def select_next_city(self):
        p_next_city = [ 0.0 for i in range(city_num) ]         #储存选择下一城市的概率
        p_all = 0.0         #所有城市的总概率
        next_city = -1      #储存下一个访问城市的序号

        for i in range(city_num):
            if self.can_visit_city[i] == True:
                #P = 信息素浓度^ALPHA / 两城市间距离^BETA
                p_next_city[i] = pow(pheromone_graph[self.current_city][i], ALPHA) * pow((1.0/distance_graph[self.current_city][i]), BETA)
                p_all += p_next_city[i]

        #用轮盘赌法选择下一城市
        if p_all >0 :
            p = random.uniform(0.0, p_all)         #随机生成一个概率
            for i in range(city_num):
                if self.can_visit_city[i] == True:
                    p -=p_next_city[i]
                    if p < 0:
                        next_city = i;
                        break
        
        #如果用上述选择方法没有选出下一个访问的城市，则在剩下的可访问城市中随机选择一个即可
        if next_city == -1:
            next_city = random.randint(0,city_num - 1)
            while (self.can_visit_city[next_city] == False):
                next_city == random.randint(0,city_num - 1)

        #方法返回选择的下一个城市
        return next_city;

#计算该蚂蚁经过的总路径长
    def add_distance(self):
        temp_distance = 0.0

        for i in range(1, city_num):        #计算路径中所有相邻访问城市间的距离
            start = self.path[i]
            end = self.path[i-1]
            temp_distance += distance_graph[start][end]

        end = self.path[0]          #计算path列表中最后访问的城市回到起点的距离
        temp_distance += distance_graph[start][end]
        self.total_distance = temp_distance

#选择完成后即可移动至下一城市
    def move(self, next_city):
        self.path.append(next_city)        #路径增加新访问的城市
        self.can_visit_city[next_city] = False            #将新访问的城市置为不可访问
        self.current_city = next_city       #改变当前停留的城市
        self.move_count += 1               #移动次数加1

#调用上述方法，开始这只蚂蚁的一生
    def lets_go(self):
        #蚂蚁出生
        self.clean_data()
        #开始探索，直到遍历完所有城市为止
        while self.move_count < city_num:
            # 移动到下一个城市
            next_city =  self.select_next_city()
            self.move(next_city)
        # 计算路径总长度
        self.add_distance()

#主函数开始
#生成48只蚂蚁
ants = [ Ant(ID) for ID in range(ant_num) ]
gen = 0         #初始化迭代次数
min_length = 1 <<31         #初始化最优解
best_path = []          #储存最优解对应的路线
best_solve_trend = []               #为可视化服务的列表
trend_x = []

while gen <MAX_GEN:         #开始迭代，最大次数为MAX_GEN 
   #每一次迭代中，找到当次的最优解
    for ant in ants:
        ant.lets_go()
        if ant.total_distance < min_length:
            min_length = ant.total_distance
            best_path = ant.path
    best_solve_trend.append(min_length)         #观察最优解收敛趋势的列表
   
   #更新信息素
   #temp_pheromone列表储存每一次循环中城市i到城市j之间信息素的改变值，易知：δij = δji
    temp_pheromone = [[0.0 for col in range(city_num)] for raw in range(city_num)]
    for ant in ants:
       for i in range(1,city_num):          #对于某只蚂蚁的路径
           start = ant.path[i-1]
           end = ant.path[i]
           # 在路径上的每两个相邻城市间留下信息素，与路径总距离反比：δ = ∑（Q / Lk）
           temp_pheromone[start][end] += Q / ant.total_distance
           temp_pheromone[end][start] = temp_pheromone[start][end]
   #总信息素为原信息素(pheromone_graph)加上改变的信息素(temp_pheromone)
   #乘以RHO表示信息素挥发后剩下的部分
    for i in range(city_num):
       for j in range(city_num):
          pheromone_graph[i][j] = pheromone_graph[i][j] * RHO + temp_pheromone[i][j]  
    #迭代次数加1
    gen+=1          

#输出最短路径长度
print('最短路径长度为：'+str(min_length))
#输出最优路线规划
print('最优路线规划为：'+str(best_path))


#算法结果可视化处理
fig1 = plt.figure()              #创建画板
image = plt.imread('res.jpg')
ax1 = fig1.add_subplot(111)              #第一个图，最佳路径图
ax1.set(xlim=[0, 4000], ylim=[2697, 0], title='the best TSP path', ylabel='Y-Axis', xlabel='X-Axis')               #设定图一x，y轴
ax1 = plt.imshow(image)

ax1 = plt.scatter(distance_x, distance_y, s = 8.0, color = 'black')                 #画点：32个城市
#画best_path，即按顺序将50个点连接起来
for i in range(1,city_num):         
    start = best_path[i-1]
    end = best_path[i]
    x = [ [distance_x[start], distance_x[end]] ]
    y = [ [distance_y[start], distance_y[end]] ]
    for j in range(len(x)):
        ax1= plt.plot(x[j], y[j], color='r')
#连接起点和最后一个访问的城市  
start = best_path[0]
x = [ [distance_x[start], distance_x[end]] ]
y = [ [distance_y[start], distance_y[end]] ]
ax1 = plt.plot(x[0], y[0], color = 'r')

fig2 = plt.figure()
ax2 = fig2.add_subplot(111)              #第二个图，最优解收敛图
ax2.set(xlim=[0, 400], ylim=[9000, 20000], title='Convergence graph of optimal solution', ylabel='Y-Axis', xlabel='X-Axis')             #设定图二x，y轴
#做最优解的收敛趋势图
for i in range(400):
    trend_x.append(i)
nx = np.array(trend_x)
ny = np.array(best_solve_trend)
ax2 = plt.plot(nx, ny, c = 'r') 
ax2 = plt.scatter(nx, ny, s = 1.0, color = 'black') 

#输出画板
plt.show()