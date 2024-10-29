# lab.py


import pandas as pd
import numpy as np
import io
from pathlib import Path
import os


# ---------------------------------------------------------------------
# QUESTION 1
# ---------------------------------------------------------------------


def prime_time_logins(login):
    login_copy = login.assign(Time=pd.to_datetime(login['Time']))
    return (login_copy
            .assign(Time=(login_copy['Time'].dt.hour>=16)
                     & (login_copy['Time'].dt.hour<20))
            .groupby('Login Id').sum())



# ---------------------------------------------------------------------
# QUESTION 2
# ---------------------------------------------------------------------


def count_frequency(login):
    def get_freq(times):
        times = pd.to_datetime(times)
        return times.count()/((pd.Timestamp('2024-01-31 23:59:00')-times.min()).days)
    return login.groupby('Login Id')['Time'].agg(get_freq)

# ---------------------------------------------------------------------
# QUESTION 3
# ---------------------------------------------------------------------


def cookies_null_hypothesis():
    return [1,2]
                         
def cookies_p_value(N):
    cookies = [0.04,0.96]
    num_cookies = 250
    obs_statistic = 15
    simulations = np.random.multinomial(num_cookies,cookies,size=N)
    return float(np.mean(simulations[:,0]>=obs_statistic))



# ---------------------------------------------------------------------
# QUESTION 4
# ---------------------------------------------------------------------


def car_null_hypothesis():
    return [1, 4]

def car_alt_hypothesis():
    return [2, 6]

def car_test_statistic():
    return [1,4]

def car_p_value():
    return 4


# ---------------------------------------------------------------------
# QUESTION 5
# ---------------------------------------------------------------------


def superheroes_test_statistic():
    return [1,2]
    
def bhbe_col(heroes):
    return (heroes['Hair color'].str.lower().str.contains('blond') 
            &heroes['Eye color'].str.lower().str.contains('blue'))

def superheroes_observed_statistic(heroes):
    return heroes[bhbe_col(heroes)]['Alignment'].value_counts(normalize=True).get('good')

def simulate_bhbe_null(heroes, N):
    num_bb = bhbe_col(heroes).sum()
    sample_prop = (heroes['Alignment'] == 'good').mean()
    sim = np.random.binomial(num_bb,sample_prop,N)
    return sim/num_bb

def superheroes_p_value(heroes):
    sims = simulate_bhbe_null(heroes,100000)
    p = float(np.mean(sims >= superheroes_observed_statistic(heroes)))
    signifigance_lvl = 0.01
    if p < signifigance_lvl:
        return [p,'Reject']
    else:
        return [p,'Fail to reject']


# ---------------------------------------------------------------------
# QUESTION 6
# ---------------------------------------------------------------------


def diff_of_means(data, col='orange'):
    return np.abs(data.loc[data['Factory']=='Yorkville',col].mean(skipna=True)
                   - data.loc[data['Factory']=='Waco',col].mean(skipna=True))


def simulate_null(data, col='orange'):
    original = data['Factory']
    data['Factory'] = np.random.permutation(data['Factory'])
    sim_stat = diff_of_means(data,col)
    data['Factory'] = original
    return sim_stat


def color_p_value(data, col='orange'):
    observed = diff_of_means(data,col)
    result = []
    for i in range(1000):
        result.append(simulate_null(data,col))
    return float(np.mean(result >= observed))



# ---------------------------------------------------------------------
# QUESTION 7
# ---------------------------------------------------------------------


def ordered_colors():
    return [('green', 0.491),
            ('orange', 0.053),
            ('purple', 0.984),
            ('red', 0.221),
            ('yellow', 0.0)][::-1]


# ---------------------------------------------------------------------
# QUESTION 8
# ---------------------------------------------------------------------


    
def same_color_distribution():
    return (0.005,'Reject')



# ---------------------------------------------------------------------
# QUESTION 9
# ---------------------------------------------------------------------


def perm_vs_hyp():
    return ['P','P','H','H','P']
