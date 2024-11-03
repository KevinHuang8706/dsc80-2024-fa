# lab.py


from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats


# ---------------------------------------------------------------------
# QUESTION 1
# ---------------------------------------------------------------------


def after_purchase():
    return ['NMAR','MD','MAR','MAR',"MAR"]


# ---------------------------------------------------------------------
# QUESTION 2
# ---------------------------------------------------------------------


def multiple_choice():
    return ['MAR','MAR','MD','NMAR','MCAR']


# ---------------------------------------------------------------------
# QUESTION 3
# ---------------------------------------------------------------------



def first_round():
    return [0.169,'NR']
    


def second_round():
    return[0.0234,'R','D']


# ---------------------------------------------------------------------
# QUESTION 4
# ---------------------------------------------------------------------


def verify_child(heights):
    def run_test(s1,s2):
        shuffled = s2.isna()
        return stats.ks_2samp(s1[shuffled].dropna(),s1[~shuffled].dropna()).pvalue
    return heights.iloc[:,2:].apply(lambda x:run_test(heights['father'],x))


# ---------------------------------------------------------------------
# QUESTION 5
# ---------------------------------------------------------------------


def cond_single_imputation(new_heights):
    new_heights['bin'] = pd.qcut(new_heights['father'],q=4,duplicates='drop')
    mean_bin = new_heights.groupby('bin')['child'].transform('mean')
    return new_heights['child'].fillna(mean_bin)


# ---------------------------------------------------------------------
# QUESTION 6
# ---------------------------------------------------------------------


def quantitative_distribution(child, N):
    hist,bin = np.histogram(child.dropna(),bins=10,density=True)
    prob = hist*np.diff(bin)
    result = []
    for _ in range(N):
        bin_chosen_ix = np.random.choice(len(hist),p=prob)
        start,end = bin[bin_chosen_ix],bin[bin_chosen_ix+1]
        random_val = np.random.uniform(start,end)
        result.append(random_val)
    return np.array(result)

def impute_height_quant(child):
    impute = quantitative_distribution(child,len(child))
    imputed_child = child.copy()
    imputed_child[imputed_child.isna()] = impute[imputed_child.isna()]
    return imputed_child


# ---------------------------------------------------------------------
# QUESTION 7
# ---------------------------------------------------------------------


def answers():
    return [1,2,2,1], ['https://www.zillow.com/robots.txt','https://www.instagram.com/robots.txt']
