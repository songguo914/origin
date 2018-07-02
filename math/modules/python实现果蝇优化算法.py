#-*- coding:utf-8 -*-
import random


def foa( maxgen, sizepop, obj_func):
    '''
    @summary: 果蝇优化算法 Fruit Fly Optimization Algorithm
    @param maxgen: 迭代次数
    @param sizepop: 种群规模
    '''
    #随机初始果蝇群里位置
    X_axis = 10 * random.random()
    Y_axis = 10 * random.random()

    X=range(sizepop); Y=range(sizepop)
    D=range(sizepop); S=range(sizepop)
    Smell=range(sizepop)
    
    yy=range(maxgen)
    Xbest=range(maxgen)
    Ybest=range(maxgen)

    # 果蝇寻优开始，利用嗅觉寻找食物
    for i in range(sizepop):
        #赋予果蝇个体利用嗅觉搜寻食物之随机方向与距离
        X[i] = X_axis + 2 * random.random() - 1;
        Y[i] = Y_axis + 2 * random.random() - 1;

#         #由于无法得知食物位置，因此先估计与原点的距离（Dist），再计算味道浓度判定值（S），此值为距离的倒数
#         D[i] = (X[i]**2 + Y[i]**2)**0.5;
#         S[i] = 1 / D[i];
#         # 味道浓度判定值（S）代入味道浓度判定函数（或称为Fitness function），以求出该果蝇个体位置的味道浓度（Smell(i))
#         Smell[i] = obj_func(S[i]);
        Smell[i] = obj_func(X[i], Y[i])

    # 找出此果蝇群里中味道浓度最低的果蝇（求极小值）
    bestSmell = min(Smell);
    bestindex = Smell.index(bestSmell)

    #保留最佳味道浓度值与x，y的坐标，此时果蝇群里利用视觉往该位置飞去
    X_axis = X[bestindex];
    Y_axis = Y[bestindex];
    Smellbest = bestSmell;

    #果蝇迭代寻优开始
    for g in range(maxgen):
        #赋予果蝇个体利用嗅觉搜寻食物的随机方向和距离
        for i in range(sizepop):
            X[i] = X_axis + 2 * random.random() - 1;
            Y[i] = Y_axis + 2 * random.random() - 1;

#             #由于无法得知食物位置，因此先估计与原点的距离（Dist），再计算味道浓度判定值（S），此值为距离的倒数
#             D[i] = (X[i]**2 + Y[i]**2)**0.5;
#             S[i] = 1 / D[i];
#             #味道浓度判定值（S）代入味道浓度判定函数，以求出该果蝇个体位置的味道浓度（Smell(i))
#             Smell[i] = obj_func(S[i]);
            Smell[i] = obj_func(X[i], Y[i])

        #找出此果蝇群里中味道浓度最低的果蝇（求极小值）
        bestSmell = min(Smell);
        bestindex = Smell.index(bestSmell)

        #判断味道浓度是否优于前一次迭代味道浓度，若是则保留最佳味道浓度值与x，y的坐标，此时果蝇群体利用视觉往该位置飞去
        if bestSmell < Smellbest:
            X_axis = X[bestindex];
            Y_axis = Y[bestindex];
            Smellbest = bestSmell;

        #每次最优Semll值记录到yy数组中，并记录最优迭代坐标
        yy[g] = Smellbest;
        Xbest[g] = X_axis;
        Ybest[g] = Y_axis;
    return yy, Xbest, Ybest

def test_obj_func1(x, y):
    '''
    @summary: 可以求出s**2 -3等类似的单变量函数的极小值
    '''
    #由于无法得知食物位置，因此先估计与原点的距离（Dist），再计算味道浓度判定值（S），此值为距离的倒数
    d = (x**2 + y**2)**0.5
    s = 1.0 / d
    # 味道浓度判定值（S）代入味道浓度判定函数（或称为Fitness function），以求出该果蝇个体位置的味道浓度（Smell(i))
    
    return s**2 - 3

def test_obj_func2(x, y):
    '''
    @summary: 可以求出x**2 + y**2 + 4的极小值
    '''
    return x**2 + y**2 + 4

if "__main__" == __name__:
    yy, Xbest, Ybest = foa(20, 10, test_obj_func1)
    print yy[-1]
    yy, Xbest, Ybest =  foa(30, 10, test_obj_func2)
    print yy[-1]
