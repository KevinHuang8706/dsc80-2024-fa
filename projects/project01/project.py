# project.py


import pandas as pd
import numpy as np
from pathlib import Path

import plotly.express as px


# ---------------------------------------------------------------------
# QUESTION 1
# ---------------------------------------------------------------------


def get_assignment_names(grades):
    result = {"lab":[],"project":[],"midterm":[],"final":[],"disc":[],"checkpoint":[]}
    for column in grades.columns:
        if column.startswith("discussion") and len(column) == 11:
            result['disc'].append(column)
            continue
        elif column.startswith('project') and len(column) == 9: 
#(('free_response' in column and len(column) == 23) or len(column) == 9):
            result['project'].append(column)
        for key in result:
            if column.lower() == key or (key in column.lower() and column[-2:].isdigit()):
                result[key].append(column) if column not in result[key] else None
    result['project'] = [i for i in result['project'] if i not in result['checkpoint']]
    return result
        


# ---------------------------------------------------------------------
# QUESTION 2
# ---------------------------------------------------------------------


def projects_total(grades):
    total = pd.Series(0,index = grades.index)
    projects = get_assignment_names(grades)['project']
    project_counts = len(projects)
    for project in projects:
        if project+'_free_response' in grades.columns:
            score = grades[project+'_free_response'].fillna(0) + grades[project].fillna(0)
            max_score = (grades[project+'_free_response - Max Points']
                          + grades[project+' - Max Points'])
        else:
            score = grades[project].fillna(0)
            max_score =  grades[project+' - Max Points']
        total += score/max_score
    return total/project_counts

# ---------------------------------------------------------------------
# QUESTION 3
# ---------------------------------------------------------------------


def lateness_penalty(col):
    def calculate_penalty(cell):
        time = list(map(lambda x: int(x),cell.split(":")))
        late_time = time[0]*3600+time[1]*60+time[2]
        if late_time <= 2*3600:
            return 1
        elif late_time <= 7*24*3600:
            return 0.9
        elif late_time <= 14*24*3600:
            return 0.7
        else:
            return 0.4
    return col.apply(calculate_penalty)


# ---------------------------------------------------------------------
# QUESTION 4
# ---------------------------------------------------------------------


def process_labs(grades):
    ret = pd.DataFrame()
    for lab in get_assignment_names(grades)['lab']:
        ret[lab] = grades[lab].fillna(0)/grades[lab+' - Max Points']\
            *lateness_penalty(grades[lab+' - Lateness (H:M:S)'])
    return ret


# ---------------------------------------------------------------------
# QUESTION 5
# ---------------------------------------------------------------------


def lab_total(processed):
    def remove_min_avg(row):
        return (row.sum() - row.min())/(len(row) - 1)
    return processed.apply(remove_min_avg,axis=1)


# ---------------------------------------------------------------------
# QUESTION 6
# ---------------------------------------------------------------------


def total_points(grades):
    def get_assignment_grade(assignments):
        grade_total = pd.Series(0,index=grades.index)
        for assignment in assignments:
            grade_total += grades[assignment].fillna(0)/grades[assignment+" - Max Points"]
        return grade_total/len(assignments)
    categories = get_assignment_names(grades)
    lab = lab_total(process_labs(grades))*0.2
    project = projects_total(grades)*0.3
    midterm_grades = (grades['Midterm'].fillna(0)/grades['Midterm - Max Points'])*0.15
    final_grades = (grades['Final'].fillna(0)/ grades['Final - Max Points'])*0.3
    checkpoint = get_assignment_grade(categories['checkpoint'])*0.025
    discussion = get_assignment_grade(categories['disc'])*0.025
    return lab+midterm_grades+project+final_grades+checkpoint+discussion


# ---------------------------------------------------------------------
# QUESTION 7
# ---------------------------------------------------------------------


def final_grades(total):
    def assign_grade(grade):
        if grade >= .9:
            return 'A'
        elif grade >= .8:
            return 'B'
        elif grade >= .7: 
            return 'C'
        elif grade >= .6: 
            return 'D'
        else: 
            return 'F'
    return total.apply(assign_grade)

def letter_proportions(total):
    return final_grades(total).value_counts(normalize=True)


# ---------------------------------------------------------------------
# QUESTION 8
# ---------------------------------------------------------------------


def raw_redemption(final_breakdown, question_numbers):
    point_sum = pd.Series(0,index=final_breakdown.index,dtype=float)
    max_point =0
    for q in question_numbers:
        point_sum += final_breakdown.iloc[:,q].fillna(0)
        max_point += final_breakdown.iloc[:,q].max()
    return pd.DataFrame({
        'PID':final_breakdown.iloc[:,0],
        'Raw Redemption Score': point_sum/max_point
        })
    
def combine_grades(grades, raw_redemption_scores):
    return grades.merge(raw_redemption_scores,left_on='PID',right_on='PID',how='left')


# ---------------------------------------------------------------------
# QUESTION 9
# ---------------------------------------------------------------------


def z_score(ser):
    if ser.std(ddof=0)==0:
        return pd.Series(0,index=ser.index)
    else:
        return (ser-ser.mean())/ser.std(ddof=0)
    
def add_post_redemption(grades_combined):
    cleaned_midterm = grades_combined['Midterm'].fillna(0)
    mt_prop = cleaned_midterm/grades_combined['Midterm - Max Points']
    mt_z = z_score(mt_prop)
    redem_z = z_score(grades_combined['Raw Redemption Score'])
    post_redem = pd.Series(max(a,b) for a,b in zip(redem_z,mt_z))*np.std(mt_prop,ddof=0)+mt_prop.mean()
    grades_combined['Midterm Score Pre-Redemption'] = mt_prop
    grades_combined['Midterm Score Post-Redemption'] = post_redem
    return grades_combined


# ---------------------------------------------------------------------
# QUESTION 10
# ---------------------------------------------------------------------


def total_points_post_redemption(grades_combined):
    with_redemption = add_post_redemption(grades_combined)
    pre_adjust = total_points(grades_combined)
    post_adjust = (pre_adjust - with_redemption['Midterm Score Pre-Redemption'] * 0.15
                    + with_redemption['Midterm Score Post-Redemption'] * 0.15)
    return post_adjust

        
def proportion_improved(grades_combined):
    def to_interval(grade):
        if grade >= 0.9:
            return 'A'
        elif grade >= 0.8:
            return 'B'
        elif grade >= 0.7:
            return 'C'
        elif grade >= 0.6:
            return 'D'
        else:
            return 'F'
    pre_adjust = total_points(grades_combined).apply(to_interval)
    post_adjust = total_points_post_redemption(grades_combined).apply(to_interval)
    improved = (post_adjust < pre_adjust)
    return improved.sum()/len(grades_combined)


# ---------------------------------------------------------------------
# QUESTION 11
# ---------------------------------------------------------------------


def section_most_improved(grades_analysis):
    def proportion_improved(pre,post):
        return (((post*10).astype(int)-(pre*10).astype(int))>=1).mean()
    improvement =  (grades_analysis
                    .groupby('Section')
                    .apply(
                        lambda x:proportion_improved(x['Total Points Pre-Redemption'],\
                                                     x['Total Points Post-Redemption'])))
    
    return improvement.idxmax()
def top_sections(grades_analysis, t, n):
    w_sections = (grades_analysis[grades_analysis['Final']
                                  >=grades_analysis['Final - Max Points']*t]
                                  .groupby('Section')
                                  ['PID'].count())
    return np.array(w_sections[w_sections>=n].index)

# ---------------------------------------------------------------------
# QUESTION 12
# ---------------------------------------------------------------------


def rank_by_section(grades_analysis):
    sort = (grades_analysis
            .sort_values(['Section','Total Points Post-Redemption'],ascending=[True,False]))
    sort['Section Rank'] = (sort
                            .groupby('Section')
                            .cumcount()+1)
    pivoted = (sort
               .pivot(index='Section Rank',columns='Section',values='PID')
               .fillna(''))
    return pivoted






# ---------------------------------------------------------------------
# QUESTION 13
# ---------------------------------------------------------------------


def letter_grade_heat_map(grades_analysis):
    def proportion_list(distri):
        result = distri.value_counts(normalize=True).reindex(['A','B','C','D','F'],fill_value=0)
        return result.to_list()
    sections = grades_analysis['Section'].sort_values().unique()
    letters = ['A', 'B', 'C', 'D', 'F']
    grouped = (grades_analysis
               .groupby("Section")
               ['Letter Grade Post-Redemption']
               .apply(proportion_list))
    matrix = np.array(grouped.to_list())
    fig = px.imshow(
        matrix.T,
        labels=dict(x='Section',y='Letter Grade Post-Redemption',color='color'),
        x = sections,
        y = letters,
        color_continuous_scale="YlGnBu", 
    )
    fig.update_layout(
        title = 'Distribution of Letter Grades by Section',
        xaxis_title = 'Section',
        yaxis_title = 'Letter Grade Post-Redemption',
        font = dict(size=10),
        height = 800,
        width = 1600
    )
    return fig

