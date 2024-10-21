# lab.py


import os
import io
from pathlib import Path
import pandas as pd
import numpy as np


# ---------------------------------------------------------------------
# QUESTION 1
# ---------------------------------------------------------------------


def read_linkedin_survey(dirname):
    dirname = Path(dirname)
    if not dirname.exists() or not dirname.is_dir():
        raise FileNotFoundError()
    def rename_columns(col_name):
        return col_name.lower().replace('_', ' ')
    df = pd.DataFrame([],columns=['first name', 'last name', 'current company',
                                'job title', 'email', 'university'])
    for file in dirname.iterdir():
        file_df = pd.read_csv(file)
        file_df = file_df.rename(columns=rename_columns)
        df = pd.concat([df,file_df],ignore_index=True)
    return df.map(lambda x:x.strip('"') if isinstance(x,str) else x)


def com_stats(df):
    ohio_cs = ((df['university'].str.contains('Ohio')
               &df['job title'].str.contains('Programmer'))
               .mean())
    engineers = (df
                 .loc[df['job title'].fillna('').str.endswith('Engineer')
                      ,'job title']
                 .nunique())
    longest = df.loc[df['job title'].fillna('').apply(len).idxmax(),'job title']
    managers = df['job title'].str.lower().str.contains('manager').sum()
    return [ohio_cs,engineers,longest,managers]


# ---------------------------------------------------------------------
# QUESTION 2
# ---------------------------------------------------------------------


def read_student_surveys(dirname):
    dirname = Path(dirname)
    if not dirname.exists() or not dirname.is_dir():
        raise FileNotFoundError()
    files = dirname.iterdir()
    df = pd.DataFrame()
    for file in files:
        survey_df = pd.read_csv(file)
        if df.empty:
            df = survey_df
        else:
            df = df.merge(survey_df,on='id',how='left')
    return df.set_index('id')


def check_credit(df):
    df = df.replace('(no genres listed)',np.nan)
    result = pd.DataFrame(index=df.index).assign(name=df['name'])
    def count_credit_student(row):
        ec_5 = row.drop('name').notnull().sum() > 0.5*len(row.drop('name'))
        return ec_5*5
    for_all = min((df.notnull().mean() > 0.9).sum()-1,2)
    result['ec'] = df.apply(count_credit_student,axis=1) + for_all
    return result
    


# ---------------------------------------------------------------------
# QUESTION 3
# ---------------------------------------------------------------------


def most_popular_procedure(pets, procedure_history):
    merged_df = pets.merge(procedure_history,on='PetID',how='left')
    return merged_df['ProcedureType'].value_counts().idxmax()

def pet_name_by_owner(owners, pets):
    return (owners
            .merge(pets,on='OwnerID',how='left')
            .groupby(['OwnerID','Name_x'])['Name_y']
            .agg(lambda x:x.to_list() if len(x)>1 else x)
            .reset_index()
            .drop(['OwnerID'],axis=1)
            .set_index('Name_x')
            ['Name_y'])


def total_cost_per_city(owners, pets, procedure_history, procedure_detail):
    merged_df = (owners
                 .merge(pets,on='OwnerID',how='left')
                 .merge(procedure_history,on='PetID',how='left')
                 .merge(procedure_detail,on=['ProcedureType','ProcedureSubCode']
                        ,how='left'))
    return merged_df.groupby('City')['Price'].sum()


# ---------------------------------------------------------------------
# QUESTION 4
# ---------------------------------------------------------------------


def average_seller(sales):
    return (sales.pivot_table(
        index = 'Name',
        values = 'Total',
        aggfunc = 'mean'
   )
   .rename(columns={"Total":"Average Sales"}))

def product_name(sales):
    return sales.pivot_table(
        index = 'Name',
        columns = 'Product',
        values = 'Total',
        aggfunc = 'sum'
    )

def count_product(sales):
    return (sales.pivot_table(
        index = ['Product','Name'],
        columns = 'Date',
        values = 'Total',
        aggfunc = 'sum'
    )
    .fillna(0))

def total_by_month(sales):
    sales['Month'] = (pd
                     .to_datetime(sales['Date'],format="%m.%d.%Y")
                     .dt.strftime('%B'))
    return (sales.pivot_table(
        index = ['Name','Product'],
        columns = 'Month',
        values = 'Total',
        aggfunc = 'sum'
    )
    .fillna(0))
