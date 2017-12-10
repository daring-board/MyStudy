import os
import pulp
import pandas as pd
import numpy as np

def readData():
    path = './data/test.csv'
    datas = [line for line in open(path, 'r', encoding='utf-8')][1:481]
    datas = [line.split(',') for line in datas]
    datas = {row[0]:(float(row[1]), row[3], row[4]) for row in datas}
    return datas

def formData(datas):
    df = pd.DataFrame.from_dict(datas, orient='index')
    diff1 = df[0].shift(1)[1:]-df[0][1:]
    diff2 = df[0].shift(2)[2:]-df[0][2:]
    correct = df[0].shift(6)[6:]-df[0][6:]
    c_plus = correct.copy()
    for idx in range(len(c_plus)):
        if c_plus[idx] > 0.02: c_plus[idx] = 1
        else: c_plus[idx] = 0
    c_minus = correct.copy()
    for idx in range(len(c_minus)):
        if c_minus[idx] < -0.02: c_minus[idx] = 1
        else: c_minus[idx] = 0
    return diff1, diff2, c_plus, c_minus

def extractScores(datas):
    df = pd.DataFrame.from_dict(datas, orient='index')
    u_scores = df[1][1:]
    d_scores = df[2][1:]
    return u_scores, d_scores

def judge(date, scores1, scores2, correct1, correct2):
    th = 0.5
    flag = False
    pred = 1 if float(scores1[date]) > th else 0
    if pred == correct1[date]: flag = True
    pred = 1 if float(scores2[date]) > th else 0
    if pred == correct2[date]: flag = True
    return flag

if __name__=='__main__':
    datas = readData()
    diff1, diff2, c_plus, c_minus = formData(datas)
    u_scores, d_scores = extractScores(datas)
    dates = [key for key in datas.keys()]
    for span in [20, 10]:
        problem = pulp.LpProblem('Problem Name', pulp.LpMinimize)
        #problem = pulp.LpProblem('Problem Name', pulp.LpMaximize)
        W = [pulp.LpVariable('w%d'%idx, -0.5, 0.5, 'Continuous') for idx in range(1, 7)]
        t1, t2 = {}, {}
        for idx in range(len(dates)-span, len(dates)-span+10):
            date = dates[idx]
            b1_date = dates[idx-6]
            b2_date = dates[idx-7]
            b3_date = dates[idx-8]
            s1 = 1 if diff1[date] > 0 else 0
            s2 = 1 if diff2[date] > 0 and s1 == 1 else 0
            s3 = 1 if diff1[date] < 0 else 0
            s4 = 1 if diff2[date] < 0 and s3 == 1 else 0
            s5 = 1 if judge(b1_date, u_scores, d_scores, c_plus, c_minus) and judge(b2_date, u_scores, d_scores, c_plus, c_minus) else 0
            s6 = 1 if s5 == 1 and judge(b3_date, u_scores, d_scores, c_plus, c_minus) else 0
            u_sign = np.sign(float(u_scores[b1_date]) - c_plus[b1_date])
            d_sign = np.sign(float(d_scores[b1_date]) - c_minus[b1_date])
            #print('%d, %d, %d, %d, %d, %d, %d, %d'%(s1, s2, s3, s4, s5, s6, u_sign, d_sign))
            #print(u_scores[date])
            #print(d_scores[date])
            t1[idx] = pulp.LpVariable('t1_%d'%idx, 0, 1)
            t2[idx] = pulp.LpVariable('t2_%d'%idx, 0, 1)
            problem += (float(u_scores[date]) + s1*W[1] + s2*W[2] + u_sign*s5*W[4] + u_sign*s6*W[5] - c_plus[date] <= t1[idx])
            problem += (float(u_scores[date]) + s1*W[1] + s2*W[2] + u_sign*s5*W[4] + u_sign*s6*W[5] - c_plus[date] >= -t1[idx])
            problem += (float(d_scores[date]) + s3*W[2] + s4*W[3] + d_sign*s5*W[4] + d_sign*s6*W[5] - c_minus[date] <= t2[idx])
            problem += (float(d_scores[date]) + s3*W[2] + s4*W[3] + d_sign*s5*W[4] + d_sign*s6*W[5] - c_minus[date] >= -t2[idx])
        expr = None
        for idx in range(len(dates)-span, len(dates)-span+5): expr += (t1[idx] + t2[idx])
        problem += expr
        print(problem)
        status = problem.solve()
        #print(status)
        for v in problem.variables(): print('%s=%.2f'%(v.name, v.varValue))
    #    delta = [pulp.LpVariable('w%d'%idx, 0, 1, 'Integetr') for idx in ]
