import joblib
import pandas as pd
from pydantic import BaseModel, Field
from fastapi import FastAPI
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

model = joblib.load('xg_model_room_type.plk')
Columns=['neighbourhood_group', 'neighbourhood', 'latitude', 'longitude',
       'room_type', 'price', 'minimum_nights', 'number_of_reviews',
       'reviews_per_month', 'calculated_host_listings_count',
       'availability_365']

class Features(BaseModel):
    neighbourhood_group: str = Field(..., min_length=1)
    neighbourhood: str =Field(..., min_length=1)
    latitude: float=Field(..., ge=-90,le=90)
    longitude: float= Field(...,ge=-180,le=180)
    price: float=Field(...,gt=0)
    minimum_nights: int=Field(...,ge=1,le=365)
    number_of_reviews: int=Field(...,ge=0)
    reviews_per_month: Optional[float] = None
    calculated_host_listings_count: int=Field(...,ge=0)
    availability_365: int=Field(...,ge=0,le=365)


app = FastAPI()


@app.get('/')
def greet():
    return {'message': 'Hello'}

@app.post('/predict')
def predict(features:Features):
    row= pd.DataFrame([features.dict()],columns=Columns)
    prediction= model.predict(row)
    probability= model.predict_proba(row)
    return {
       "Prediction_room_tpye": prediction[0],
       "Probability":probability.tolist()[0]
    }