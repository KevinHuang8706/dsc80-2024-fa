# project.py


import pandas as pd
import numpy as np
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
pd.options.plotting.backend = 'plotly'

from IPython.display import display

# DSC 80 preferred styles
pio.templates["dsc80"] = go.layout.Template(
    layout=dict(
        margin=dict(l=30, r=30, t=30, b=30),
        autosize=True,
        width=600,
        height=400,
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        title=dict(x=0.5, xanchor="center"),
    )
)
pio.templates.default = "simple_white+dsc80"
import warnings
warnings.filterwarnings("ignore")


# ---------------------------------------------------------------------
# QUESTION 1
# ---------------------------------------------------------------------


def clean_loans(loans):
    def convert_date(loans):
        loans['issue_d'] = pd.to_datetime(loans['issue_d'],format="%b-%Y")
        return loans
    def term_len(loans):
        loans['term'] = loans['term'].str.strip(" months").astype(int)
        return loans
    def clean_title(loans):
        loans['emp_title'] = loans['emp_title'].str.strip().str.lower()
        loans.loc[loans['emp_title']=='rn','emp_title'] = 'registered nurse'
        return loans
    def create_term_end(loans):
        loans['term_end'] = [d+pd.DateOffset(months=m) for d,m in 
                             zip(loans['issue_d'],loans['term'])]
        return loans
    return (loans
            .pipe(convert_date)
            .pipe(term_len)
            .pipe(clean_title)
            .pipe(create_term_end))


# ---------------------------------------------------------------------
# QUESTION 2
# ---------------------------------------------------------------------



def correlations(df, pairs):
    result = pd.Series()
    for pair in pairs:
        if pair[0] in df.columns and pair[1] in df.columns:
            r_corr = (df[[pair[0],pair[1]]]
                      .corr(method='pearson')
                      .loc[pair[0]].get(pair[1]))
            result['r_'+'_'.join(pair)] = r_corr
    return result




# ---------------------------------------------------------------------
# QUESTION 3
# ---------------------------------------------------------------------


def create_boxplot(loans):
    brackets = [580, 670, 740, 800, 850]
    labels = ["[580, 670)","[670, 740)","[740, 800)","[800, 850)"]
    loans_copy = loans.copy().sort_values(by='fico_range_low')
    loans_copy['Credit_score_range'] = pd.cut(loans_copy['fico_range_low'], bins=brackets, labels=labels, right = False)
    loans_copy['Credit_score_range'] = pd.Categorical(loans_copy['Credit_score_range'],categories=labels,ordered=True)
    fig = px.box(loans_copy,x='Credit_score_range',y='int_rate',color='term',
                 color_discrete_map={36:'purple',60:'gold'},
                 labels = {
                     'int_rate': 'Interest Rate (%)',
                     'Credit_score_range': 'Credit Score Range',
                     'term': 'Loan Length (Months)'
                 },
                 title = 'Interest Rate vs. Credit Score')
    fig.update_layout(
        yaxis=dict(range=[5, 33]),
        boxmode = 'group'
    )
    return fig

# ---------------------------------------------------------------------
# QUESTION 4
# ---------------------------------------------------------------------


def ps_test(loans, N):
    mask = loans['desc'].isna()
    observed = loans.loc[~mask,'int_rate'].mean() - loans.loc[mask,'int_rate'].mean()
    result = []
    for _ in range(N):
        shuffled = np.random.permutation(mask)
        result.append(loans[~shuffled]['int_rate'].mean() - loans[shuffled]['int_rate'].mean())
    return np.mean(result>=observed)



def missingness_mechanism():
    return 2
    
def argument_for_nmar():
    return '''
    The personal statement can also be NMAR because some people may not provide
    a personal statement because they don't have an uncommon reason for a loan
    such as an urgent vet bill
    '''


# ---------------------------------------------------------------------
# QUESTION 5
# ---------------------------------------------------------------------


def tax_owed(income, brackets):
    i = 0
    tax = 0.0
    while i < len(brackets) and income > brackets[i][1]:
        tax += (min(brackets[i+1][1] if i < len(brackets) -1 else float('inf'),income) - brackets[i][1])*brackets[i][0]
        i += 1
    return tax


# ---------------------------------------------------------------------
# QUESTION 6
# ---------------------------------------------------------------------


def clean_state_taxes(state_taxes_raw): 
    state_taxes_raw = state_taxes_raw.dropna(how='all')
    state_taxes_raw['State'] = (state_taxes_raw['State']
                                .where(~state_taxes_raw['State'].astype(str).str.contains(r'[\(\)]'),np.nan)
                                .fillna(method='ffill'))
    state_taxes_raw['Rate'] = (state_taxes_raw['Rate']
                               .str.replace('none','0.00%')
                               .str.strip("%").astype(float)/100)
    state_taxes_raw['Rate'] = state_taxes_raw['Rate'].round(2)
    state_taxes_raw['Lower Limit'] = (state_taxes_raw['Lower Limit']
                                      .fillna('$0')
                                      .str.strip("$")
                                      .str.replace(',','')
                                      .astype(int))
    return state_taxes_raw




# ---------------------------------------------------------------------
# QUESTION 7
# ---------------------------------------------------------------------


def state_brackets(state_taxes):
    combined = state_taxes.groupby('State').apply(lambda x: list(zip(x['Rate'], x['Lower Limit'])))
    return pd.DataFrame(combined,columns=['bracket_list'])
    
def combine_loans_and_state_taxes(loans, state_taxes):
    # Start by loading in the JSON file.
    # state_mapping is a dictionary; use it!
    import json
    state_mapping_path = Path('data') / 'state_mapping.json'
    with open(state_mapping_path, 'r') as f:
        state_mapping = json.load(f)
    # Now it's your turn:
    state_taxes_copy = state_brackets(state_taxes).copy().reset_index()
    state_taxes_copy['State'] = state_taxes_copy['State'].replace(state_mapping)
    return (loans
            .rename(columns={'addr_state':'State'})
            .merge(state_taxes_copy,on = 'State',how = 'left'))


# ---------------------------------------------------------------------
# QUESTION 8
# ---------------------------------------------------------------------


def find_disposable_income(loans_with_state_taxes):
    FEDERAL_BRACKETS = [
     (0.1, 0), 
     (0.12, 11000), 
     (0.22, 44725), 
     (0.24, 95375), 
     (0.32, 182100),
     (0.35, 231251),
     (0.37, 578125)
    ]
    fed_tax = loans_with_state_taxes['annual_inc'].apply(lambda x:tax_owed(x,FEDERAL_BRACKETS))
    state_tax = loans_with_state_taxes.apply(lambda x:tax_owed(x['annual_inc'],x['bracket_list']),axis=1)
    disposable_income = (loans_with_state_taxes['annual_inc']- fed_tax - state_tax)
    result = loans_with_state_taxes.copy()
    result['federal_tax_owed'] = fed_tax
    result['state_tax_owed'] = state_tax
    result['disposable_income'] = disposable_income
    return result

# ---------------------------------------------------------------------
# QUESTION 9
# ---------------------------------------------------------------------


def aggregate_and_combine(loans, keywords, quantitative_column, categorical_column):
    query = loans.copy()
    forged_names = []
    query['temp'] = query['emp_title']
    for keyword in keywords:
        query.loc[query['emp_title'].str.contains(keyword),'temp'] = f"{keyword}_mean_{quantitative_column}"
        forged_names.append(f"{keyword}_mean_{quantitative_column}")
    result = query[query['temp'].isin(forged_names)].pivot_table(
        index = categorical_column,
        values = quantitative_column,
        columns = 'temp',
        aggfunc = 'mean'
    )
    result.loc['Overall'] = query[query['temp'].isin(forged_names)].groupby('temp')[quantitative_column].mean()
    return result


# ---------------------------------------------------------------------
# QUESTION 10
# ---------------------------------------------------------------------


def exists_paradox(loans, keywords, quantitative_column, categorical_column):
    diff = aggregate_and_combine(loans,keywords,quantitative_column,categorical_column)
    if diff.shape[1] < 2:
        return False
    #diff = diff.diff(axis=1).iloc[:,-1]
    diff = diff.iloc[:,0] - diff.iloc[:,-1]
    return not (diff.empty or len(diff) < 2) and bool(((diff[:-1] > 0).all() and diff[-1] < 0) or ((diff[:-1] < 0).all() and diff[-1] > 0))
def paradox_example(loans):
    return {
        'loans': loans,
        'keywords': ['nurse', 'engineer'],
        'quantitative_column': 'loan_amnt',
        'categorical_column': 'grade'
    }
