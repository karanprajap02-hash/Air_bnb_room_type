import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import kagglehub
import os

# Download latest version
path = kagglehub.dataset_download("dgomonov/new-york-city-airbnb-open-data")

print("Path to dataset files:", path)
ab_nyc=os.path.join(path,"AB_NYC_2019.csv")
data_df=pd.read_csv(ab_nyc)
data_df.head()

sns.boxplot(x='room_type',y='price',data=data_df)

clean_df = data_df.drop(columns=['id', 'name', 'host_id', 'host_name', 'last_review'])
clean_df['reviews_per_month'].fillna(0, inplace=True)

# Calculate the 99th percentile thresholds
price_bound = clean_df['price'].quantile(0.99)
minimum_nights_bound = clean_df['minimum_nights'].quantile(0.99)
clean_df['price'] = clean_df['price'].clip(upper=price_bound)
clean_df['minimum_nights'] = clean_df['minimum_nights'].clip(upper=minimum_nights_bound)

X=clean_df.drop(columns=['room_type'])
y=clean_df['room_type']

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.7, random_state=42)

catogrical_col=['neighbourhood_group', 'neighbourhood']
numerical_col=clean_df.select_dtypes(include=np.number).drop(columns=['latitude','longitude']).columns
spital_col=['latitude','longitude']
numerical_col

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler,PowerTransformer,RobustScaler
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer

catogarical_pipe=Pipeline(steps=[
    ('simple_imputer',SimpleImputer(strategy='most_frequent')),
    ('onehot_encoder',OneHotEncoder(handle_unknown='ignore'))
])
numeric_pipe=Pipeline(steps=[
    ('simple_imputer',SimpleImputer(strategy='median')),
    ('robust',RobustScaler()),
    ('power_trans',PowerTransformer(method='yeo-johnson')),
    ('standar_scal',StandardScaler())
])
spital_pipe=Pipeline(steps=[
    ('simple_imputer',SimpleImputer(strategy='median')),
    ('standar_scal',StandardScaler())
])

preprocesor=ColumnTransformer(transformers=[
  ('catogarical_transformer',catogarical_pipe,catogrical_col),
  ('numerical_transformer',numeric_pipe,numerical_col),
  ('spital_transformer',spital_pipe,spital_col)
])

import warnings
warnings.filterwarnings('ignore')

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier , GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score,f1_score,confusion_matrix

from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, f1_score

# XGBoost requires numerical labels
le = LabelEncoder()
y_train_encoded = le.fit_transform(y_train)
y_test_encoded = le.transform(y_test)

xgboost_model = Pipeline(steps=[
    ('preprocessor', preprocesor),
    ('xgboost_model', XGBClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1
    ))
])

# Fit the model using encoded labels
xg_model = xgboost_model.fit(X_train, y_train_encoded)

xgb_pred = xgboost_model.predict(X_test)
xgb_pred_train = xgboost_model.predict(X_train)

xgb_training = accuracy_score(y_train_encoded, xgb_pred_train)
xgb_testing = accuracy_score(y_test_encoded, xgb_pred)
xgb_f1_macro = f1_score(y_test_encoded, xgb_pred, average='macro')

print(f'Classes: {le.classes_}')
print(f'xgb_training_accuracy: {xgb_training:.3f}')
print(f'xgb_testing_accuracy: {xgb_testing:.3f}')
print(f'xgb_f1_macro: {xgb_f1_macro:.3f}')

import joblib
joblib.dump(xgboost_model,'xgboost_model_room_type22.pkl')

loaded_xgboost_model = joblib.load('xgboost_model_room_type22.pkl')
print("Model loaded successfully!")