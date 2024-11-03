# lab.py


import os
import io
from pathlib import Path
import pandas as pd
import numpy as np


# ---------------------------------------------------------------------
# QUESTION 1
# ---------------------------------------------------------------------


def trick_me():
    data = [[1,2,3],
            [2,3,4],
            [4,3,2],
            [5,4,1]
    ]
    tricky1 = pd.DataFrame(data,columns=['Name','Name','Age'])
    tricky1.to_csv('tricky1.csv',index=False)
    tricky2 = pd.read_csv('tricky1.csv')
            
    return 3


def trick_bool():
    return [4,10,13]


# ---------------------------------------------------------------------
# QUESTION 2
# ---------------------------------------------------------------------


def population_stats(df):
    def transformation(col):
        num_nonnull = col.count()  # Count non-null values
        prop_nonnull = num_nonnull / len(col)  # Proportion of non-null values
        num_distinct = col.nunique()  # Number of distinct non-null values
        prop_distinct = num_distinct / num_nonnull if num_nonnull > 0 else np.nan  # Proportion of distinct non-null values

        return pd.Series({
            'num_nonnull': num_nonnull,
            'prop_nonnull': prop_nonnull,
            'num_distinct': num_distinct,
            'prop_distinct': prop_distinct
        })
    return df.apply(transformation).T


# ---------------------------------------------------------------------
# QUESTION 3
# ---------------------------------------------------------------------


def most_common(df, N=10):
    result = pd.DataFrame()
    for column in df.columns:
        top_N = (df[column]
                 .value_counts()
                 .sort_values(ascending=False)
                 .iloc[:N]
                 .reset_index()
                 .rename(columns={column:column+'_values','count':column+'_counts'})
                 .reindex(np.arange(N),fill_value=np.nan))
        result = pd.concat([result,top_N],axis=1,ignore_index=False)
    return result


# ---------------------------------------------------------------------
# QUESTION 4
# ---------------------------------------------------------------------


def super_hero_powers(powers):
    #1
    name = (powers
            .set_index('hero_names')
            .sum(axis=1)
            .sort_values(ascending=False).index[0])
    #2
    flight = (powers[powers['Flight']]
              .set_index('hero_names')
              .sum()
              .sort_values(ascending=False)
              .index[1])
    #3
    one_power = (powers
                 .set_index('hero_names')
                 [powers.set_index('hero_names').sum(axis=1)==1]
                 .sum()
                 .sort_values(ascending=False)
                 .index[0])
    return [name,flight,one_power]



# ---------------------------------------------------------------------
# QUESTION 5
# ---------------------------------------------------------------------


def clean_heroes(heroes):
    return heroes.fillna(np.nan).replace('-',np.nan).replace(-99.0,np.nan)


# ---------------------------------------------------------------------
# QUESTION 6
# ---------------------------------------------------------------------


def super_hero_stats():
    return ['Onslaught', 'DC Comics', 'bad', 'Marvel Comics', 'NBC - Heroes', 'Groot']



# ---------------------------------------------------------------------
# QUESTION 7
# ---------------------------------------------------------------------


def clean_universities(df):
    df['institution'] = df['institution'].str.replace("\n",", ")
    df[['nation','national_ranked_cleaned']]= (df['national_rank'].str.split(',',expand=True))
    df[['broad_impact','national_ranked_cleaned']] = (
        df[['broad_impact','national_ranked_cleaned']]
        .astype(int))
    df = df.drop('national_rank',axis=1)
    df.loc[df['nation'].str.lower().str.contains('czechia'),'nation'] = 'Czech Republic'
    df.loc[df['nation'].str.startswith('USA'),'nation'] = 'United States'
    df.loc[df['nation'].str.startswith('UK'),'nation'] = 'United Kingdom'
    df['is_r1_public'] = (
        (df['control'] == 'Public') &
        df['control'].notna() &
        df['city'].notna() &
        df['state'].notna()
    )
    return df
def university_info(cleaned):
    #1
    state = (cleaned
             .groupby('state')
             .filter(lambda x:len(x)>=3)
             .groupby('state')['score']
             .mean()
             .idxmin()
    )
    #2
    top = cleaned[(cleaned['world_rank']<=100)&(cleaned['quality_of_faculty']<=100)].shape[0]\
/cleaned[cleaned['world_rank']<=100].shape[0]
    #3
    private = (cleaned
               .groupby('state')
               .filter(lambda x:x['is_r1_public'].mean()<=0.5)
               .index
               .nunique())
    #4
    worst = (cleaned[(cleaned['national_ranked_cleaned']==1)]
             .set_index('institution')
             ['world_rank']
             .idxmax())
    return [state,top,private,worst]

