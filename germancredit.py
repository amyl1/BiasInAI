# -*- coding: utf-8 -*-
"""GermanCredit.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JN1omO3-XMK8ipnxrrWVl-zyWMS6X4hV

#Finance: German-Credit for assessing credit risk
The data cleaning code and conventional implementation was written building on the following project by Janio Martinez Bachmann.
https://www.kaggle.com/janiobachmann/german-credit-analysis-a-risk-perspective
However, I have reworked and adapted it to make it suitable for this project.

#Import Libraries
"""

import pandas as pd
import numpy as np 
import seaborn as sns 
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, classification_report, confusion_matrix
sns.set(rc={'figure.figsize':(11.7,8.27)})

"""#Load Dataset"""

df = pd.read_csv('german_credit_data.csv')
df = df.iloc[:, 1:]
print(df.head())

"""#Task 2 : Data Analysis

Fill the missing values. For checking account, fill with none. Then drop any rows with null values.
"""

df['Checking account'] = df['Checking account'].fillna('None')
df.dropna(inplace=True)

"""Binning age into age groups. These are in 10 year groups between 30 and 70. Then there are also groups for those under 30 and those over 70."""

for col in [df]:
    col.loc[(col['Age'] > 18) & (col['Age'] <= 29), 'Age_Group'] = 'Under 30'
    col.loc[(col['Age'] > 29) & (col['Age'] <= 40), 'Age_Group'] = '30-40'
    col.loc[(col['Age'] > 40) & (col['Age'] <= 50), 'Age_Group'] = '40-50'
    col.loc[(col['Age'] > 50)& (col['Age'] <= 60), 'Age_Group'] = '50-60'
    col.loc[col['Age'] > 60, 'Age_Group'] = 'Over 60'
df=df.sort_values(by=['Age'])

"""Look at the number of people in each age group. We can see that there are more younger applicants than older ones. For females, the highest number of applicats were under 30, for males, they are aged between 30 and 40."""

g = sns.countplot(
    x=df['Age_Group'],hue=df['Sex']
)

print("Bad risk obver 60: "+str(sum((df['Age_Group']=='Over 60') & (df['Risk']=='bad'))))
print("Number good risk: "+str(sum(df['Risk']=='good')))
print("Number bad risk: "+str(sum(df['Risk']=='bad')))

"""The graph below shows the number of people of each sex in the dataset. We can see that there are double the amount of males than females."""

g = sns.countplot(
    x=df['Sex']
)

"""Plotting a bar graph of age group and risk (raw numbers).



"""

g = sns.countplot(
    x=df['Age_Group'], hue=df['Risk']
)

"""Risk vs Age Group (proportion)"""

x, y, hue = "Age_Group", "proportion", "Risk"


(df[x]
 .groupby(df[hue])
 .value_counts(normalize=True)
 .rename(y)
 .reset_index()
 .pipe((sns.barplot, "data"), x=x, y=y, hue=hue))

"""Risk vs Sex"""

x, y, hue = "Risk", "proportion", "Sex"


(df[x]
 .groupby(df[hue])
 .value_counts(normalize=True)
 .rename(y)
 .reset_index()
 .pipe((sns.barplot, "data"), x=x, y=y, hue=hue))

"""For each sex, we can see the proportion of people applying for loans for each purpose. Females were more likely to apply for a credit loan to buy furniture and equipment then males, whereas males were much more likely to apply for loans to invest in business."""

x, y, hue = "Purpose", "proportion", "Sex"
hue_order = ["Male", "Female"]

(df[x]
 .groupby(df[hue])
 .value_counts(normalize=True)
 .rename(y)
 .reset_index()
 .pipe((sns.barplot, "data"), x=x, y=y, hue=hue))

print(df.describe())

df['Age_Group'].value_counts()[:3].index.tolist()

"""Function to calculate the number of true positives, false positivies, true negatives and false negatives. """

def positive_negative_measure(y_actual, y_pred):
    y_act=y_actual.to_numpy()
    TP = 0
    FP = 0
    TN = 0
    FN = 0
    for i in range(len(y_pred)): 
        if y_act[i]==y_pred[i]=='good':
           TP += 1
        elif y_pred[i]=='good' and y_act[i]!=y_pred[i]:
           FP += 1
        elif y_act[i]==y_pred[i]=='bad':
           TN += 1
        elif y_pred[i]=='bad' and y_act[i]!=y_pred[i]:
           FN += 1

    return(TP, FP, TN, FN)

"""# Task 3: Conventional Implementation

Import relevant modules and perform one hot encoding for X. Split into test and training sets (naively).
"""

from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
X=df[['Age_Group','Sex','Job','Housing','Saving accounts','Checking account','Credit amount','Duration','Purpose']]
y=df[['Risk']]
enc = OneHotEncoder(handle_unknown='ignore')
enc.fit(X)
X_train1, X_test1, y_train1, y_test1 = train_test_split(X, y, test_size=0.3, random_state=42)
X_train_enc1=enc.transform(X_train1).toarray()
X_test_enc1=enc.transform(X_test1).toarray()

"""Build the model"""

from sklearn import svm
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score

"""Implement gridsearchcv to see which are the optimum parameters"""

params = {'C': [0.75, 0.85, 0.95, 1], 'kernel': ['linear', 'poly', 'rbf', 'sigmoid'], 'degree': [2,3, 4, 5]}

svc_clf = svm.SVC(random_state=42)

grid_search_cv = GridSearchCV(svc_clf, params)
grid_search_cv.fit(X_train_enc1, y_train1)

print(grid_search_cv.best_params_)

predMap={
    "good":1,
    "bad":0
}

clf = svm.SVC(kernel='poly', C = 1.0, degree=2)
clf.fit(X_train_enc1,y_train1)
y_pred1 = clf.predict(X_test_enc1)
print(accuracy_score(y_test1, y_pred1))

TP, FP, TN, FN = positive_negative_measure(y_test1, y_pred1)
BER = 0.5*(FP/(TN+FP)+FN/(FN+TP))
print("Utility: "+str(1-BER))

conditions1 = [y_pred1 == 'good', y_pred1 == 'bad']
conditions2 = [y_test1 == 'good',y_test1 == 'bad']
choices = [1, 0]
y_pred1_enc = np.select(conditions1, choices)
y_test1_enc = np.select(conditions2, choices)
mean_absolute_error(y_test1_enc, y_pred1_enc)

"""Use the parameters found in the previous step to produce a model and check the accuracy. With these parameters we get an accuracy score of 0.7439."""

print(classification_report(y_test1, y_pred1))

X_test1["Risk"]=y_pred1

x, y, hue = "Age_Group", "proportion", "Risk"


(X_test1[x]
 .groupby(X_test1[hue])
 .value_counts(normalize=True)
 .rename(y)
 .reset_index()
 .pipe((sns.barplot, "data"), x=x, y=y, hue=hue))

"""Unbiased splitting. The dataset is imbalanced in terms of age and gender. We use straified splitting to combat this."""

X=df[['Age_Group','Sex','Job','Housing','Saving accounts','Checking account','Credit amount','Duration','Purpose']]
y=df[['Risk']]
enc = OneHotEncoder(handle_unknown='ignore')
enc.fit(X)
X_train2, X_test2, y_train2, y_test2 = train_test_split(X, y, test_size=0.3, random_state=42, stratify=X[['Age_Group', 'Sex']])
X_train_enc2=enc.transform(X_train2).toarray()
X_test_enc2=enc.transform(X_test2).toarray()

print(sum((X_train2['Age_Group']=='Over 60') & (y_train2['Risk']=='bad')))
print(sum((X_train2['Age_Group']=='Over 60') & (y_train2['Risk']=='good')))

params = {'C': [0.75, 0.85, 0.95, 1], 'kernel': ['linear', 'poly', 'rbf', 'sigmoid'], 'degree': [2,3, 4, 5]}

svc_clf = svm.SVC(random_state=42)

grid_search_cv = GridSearchCV(svc_clf, params)
grid_search_cv.fit(X_train_enc2, y_train2)

print(grid_search_cv.best_params_)

"""Use the parameters found in the previous step to produce a model and check the accuracy. With these parameters we get an accuracy score of 0.7317"""

clf = svm.SVC(kernel='poly', C = 1, degree=4)
clf.fit(X_train_enc2,y_train2)
y_pred2 = clf.predict(X_test_enc2)
print(accuracy_score(y_test2, y_pred2))
TP, FP, TN, FN = positive_negative_measure(y_test2, y_pred2)
BER = 0.5*(FP/(TN+FP)+FN/(FN+TP))
print("Utility: "+str(1-BER))

conditions1 = [y_pred2 == 'good', y_pred2 == 'bad']
conditions2 = [y_test2 == 'good',y_test2 == 'bad']
choices = [1, 0]

y_pred2_enc = np.select(conditions1, choices)
y_test2_enc = np.select(conditions2, choices)

mean_absolute_error(y_pred2_enc,y_test2_enc)

print(confusion_matrix(y_test2, y_pred2))
print(classification_report(y_test2, y_pred2))

X_test2["Risk"]=y_pred2

x, y, hue = "Age_Group", "proportion", "Risk"


(X_test2[x]
 .groupby(X_test2[hue])
 .value_counts(normalize=True)
 .rename(y)
 .reset_index()
 .pipe((sns.barplot, "data"), x=x, y=y, hue=hue))

"""# Task 4 - fair machine learning implementation

In order for reapair tool to work, columns must be orderable. We can keep columns with numeric and orderable categorical data. Therefore housing and purpose must be dropped.
"""

money_cat_order = pd.Categorical(['None', 'little','money' ,'quite rich' ,'rich'], ordered=True)
age_cat_order = pd.Categorical(['Under 30', '30-40','40-50' ,'50-60' ,'Over 60'], ordered=True)

X_columns=df[['Job','Saving accounts','Checking account','Credit amount','Duration']]
Y_columns=df[['Age','Sex','Age_Group']]
#sort all columns
Y_columns['Age_Group'].reindex(age_cat_order)
X_columns['Saving accounts'].reindex(money_cat_order)
X_columns['Checking account'].reindex(money_cat_order)
print(X_columns.head())

"""Repair Tool"""

def unique_value_data(columns):
  sorted_list={}
  index_lookups={}
  for col in columns:
    index_lookup={}
    sorted_list=df[col].unique()
    sorted_list.sort()
    sorted_lists[col]=sorted_list
    for value in sorted_list:
      index_lookup[value]=np.where(sorted_list == value)[0][0]
    index_lookups[col]=index_lookup
  return sorted_lists, index_lookups

import math
def median(lst):
  return (lst[math.floor(len(lst)/2)])

def repair(Y_columns,all_strat_comb, num_quantiles,sorted_lists,index_lookups,lamb):
  quantile_unit=1.0/num_quantiles
  for column in Y_columns:
    for quantile in range (0,num_quantiles):
      median_values_at_quantile = []
      entries_at_quantile = []
      #original pseudocode all_Strat_group
      for group in all_strat_comb:
        values=[]
        count=0
        for index,row in df.iterrows():
          if row['Age_Group']==group[0] and row['Sex']==group[1]:
            count+=1
            #if count>offset and count<group_offsets[group]:         
            entries_at_quantile.append([index])
            values.append(int(row['Age']))
        median_values_at_quantile.append(median(values))
      target_value=median(median_values_at_quantile)
      for entryID in entries_at_quantile:
         for index,row in df.iterrows():
          if index==entryID:
            value=row['Age']
            repair_value=(1-lamb)*value + lamb*target_value
            d1['index']['Age'] = repair_value

import itertools as it
sorted_lists={}
index_lookups={}
sorted_lists,index_lookups = unique_value_data(Y_columns)
S={'Age_Group':df['Age_Group'].unique(), 'Sex':df['Sex'].unique()}
allCols = sorted(S)
combinations = it.product(*(S[col] for col in allCols))
combinations=list(combinations)
min_count=df.shape[0]
comb_lengths={}
for comb in combinations:
  count=0 
  age_group=comb[0]
  sex=comb[1]
  for index, row in df.iterrows():
    if row['Age_Group']==age_group and row['Sex']==sex:
      count+=1
  if count == 0:
    combinations.remove(comb)
  else:
    comb_lengths[comb]=count
    if count<min_count:
      min_count=count
d1=df
repair(Y_columns,comb_lengths, min_count, sorted_lists, index_lookups, 0.9)

X=d1[['Age','Sex','Job','Housing','Saving accounts','Checking account','Credit amount','Duration','Purpose']]
y=d1[['Risk']]
enc = OneHotEncoder(handle_unknown='ignore')
enc.fit(X)
X_train3, X_test3, y_train3, y_test3 = train_test_split(X, y, test_size=0.3, random_state=42)
X_train_enc3=enc.transform(X_train3).toarray()
X_test_enc3=enc.transform(X_test3).toarray()

params = {'C': [0.75, 0.85, 0.95, 1], 'kernel': ['linear', 'poly', 'rbf', 'sigmoid'], 'degree': [2,3, 4, 5]}

svc_clf = svm.SVC(random_state=42)

grid_search_cv = GridSearchCV(svc_clf, params)
grid_search_cv.fit(X_train_enc3, y_train3)

print(grid_search_cv.best_params_)

clf = svm.SVC(kernel='poly', C = 0.85, degree=2)
clf.fit(X_train_enc3,y_train3)
y_pred3 = clf.predict(X_test_enc3)
print(accuracy_score(y_test3, y_pred3))

TP, FP, TN, FN = positive_negative_measure(y_test3, y_pred3)
BER = 0.5*(FP/(TN+FP)+FN/(FN+TP))
print("Utility: "+str(1-BER))

conditions1 = [y_pred3 == 'good', y_pred3 == 'bad']
conditions2 = [y_test3 == 'good',y_test3 == 'bad']
choices = [1, 0]

y_pred3_enc = np.select(conditions1, choices)
y_test3_enc = np.select(conditions2, choices)

mean_absolute_error(y_test3_enc, y_pred3_enc)

print(classification_report(y_test3, y_pred3))

X_test3["Risk"]=y_pred3

bins = [0, 30, 40, 50, 60, 120]
labels = ['Under 30', '30-40','40-50' ,'50-60' ,'Over 60']
X_test3['Age_Group'] = pd.cut(X_test3['Age'], bins, labels = labels,include_lowest = True)

x, y, hue = "Age_Group", "proportion", "Risk"


(X_test3[x]
 .groupby(X_test3[hue])
 .value_counts(normalize=True)
 .rename(y)
 .reset_index()
 .pipe((sns.barplot, "data"), x=x, y=y, hue=hue))