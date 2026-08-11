import joblib
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field
from fastapi import FastAPI
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

# 1. Load the model
model = joblib.load('xgboost_model_room_type21.pkl')

import sklearn.compose._column_transformer


# Fix for sklearn model compatibility
if not hasattr(
    sklearn.compose._column_transformer,
    "_RemainderColsList"
):
    class _RemainderColsList(list):
        pass

    sklearn.compose._column_transformer._RemainderColsList = _RemainderColsList


def patch_model_for_sklearn(estimator):
    # Search through pipelines
    if hasattr(estimator, 'steps'):
        for _, step in estimator.steps:
            patch_model_for_sklearn(step)
            
    # Search through column transformers
    if hasattr(estimator, 'transformers_'):
        for _, step, _ in estimator.transformers_:
            patch_model_for_sklearn(step)
            
    # FIX: Add the missing attribute to SimpleImputer
    if type(estimator).__name__ == 'SimpleImputer':
        if not hasattr(estimator, '_fill_dtype'):
            estimator._fill_dtype = np.float64

# Apply the patch immediately after loading!
patch_model_for_sklearn(model)
# =========================================================

Columns = [
    'neighbourhood_group', 'neighbourhood', 'latitude', 'longitude',
    'price', 'minimum_nights', 'number_of_reviews',
    'reviews_per_month', 'calculated_host_listings_count',
    'availability_365'
]

class Features(BaseModel):
    neighbourhood_group: str = Field(..., min_length=1)
    neighbourhood: str = Field(..., min_length=1)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    price: float = Field(..., gt=0)
    minimum_nights: int = Field(..., ge=1, le=365)
    number_of_reviews: int = Field(..., ge=0)
    reviews_per_month: Optional[float] = None
    calculated_host_listings_count: int = Field(..., ge=0)
    availability_365: int = Field(..., ge=0, le=365)

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def greet():
    return {'message': 'Server is running perfectly!'}

@app.post('/predict')
def predict(features: Features):
    try:
        data_dict = features.model_dump()
    except AttributeError:
        data_dict = features.dict()
        
    row = pd.DataFrame([data_dict], columns=Columns)
    
    # Run the prediction
    prediction = model.predict(row)
    probability = model.predict_proba(row)
    
    return {
       "Prediction_room_type": prediction[0],
       "Probability": probability.tolist()[0]
    }