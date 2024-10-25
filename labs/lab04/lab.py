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
        return times.count()/((pd.Timestamp('2024-01-31')-times.min()).days+1)
    return login.groupby('Login Id')['Time'].agg(get_freq)

# ---------------------------------------------------------------------
# QUESTION 3
# ---------------------------------------------------------------------


def cookies_null_hypothesis():
    return [1,2]
                         
def cookies_p_value(N):
    cookies = [0.04,0.96]
    num_cookies = 250
    sample_statistic = 15
    simulations = np.random.multinomial(num_cookies,cookies,size=N)
    return np.mean(simulations[:,0]>=sample_statistic)



# ---------------------------------------------------------------------
# QUESTION 4
# ---------------------------------------------------------------------


def car_null_hypothesis():
    ...

def car_alt_hypothesis():
    ...

def car_test_statistic():
    ...

def car_p_value():
    ...


# ---------------------------------------------------------------------
# QUESTION 5
# ---------------------------------------------------------------------


def superheroes_test_statistic():
    ...
    
def bhbe_col(heroes):
    ...

def superheroes_observed_statistic(heroes):
    ...

def simulate_bhbe_null(heroes, N):
    ...

def superheroes_p_value(heroes):
    ...


# ---------------------------------------------------------------------
# QUESTION 6
# ---------------------------------------------------------------------


def diff_of_means(data, col='orange'):
    ...


def simulate_null(data, col='orange'):
    ...


def color_p_value(data, col='orange'):
    ...


# ---------------------------------------------------------------------
# QUESTION 7
# ---------------------------------------------------------------------


def ordered_colors():
    ...


# ---------------------------------------------------------------------
# QUESTION 8
# ---------------------------------------------------------------------


    
def same_color_distribution():
    ...


# ---------------------------------------------------------------------
# QUESTION 9
# ---------------------------------------------------------------------


def perm_vs_hyp():
    ...
