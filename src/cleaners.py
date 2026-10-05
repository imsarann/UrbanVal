import json
import re
import ast
from typing import List
import numpy as np
import pandas as pd


def clean_price(series: pd.Series) -> pd.Series:
    cleaned = (
        series.astype(str)
        .str.replace(r'[\$,]', '', regex=True)
        .str.strip()
    )
    numeric = pd.to_numeric(cleaned, errors='coerce')
    numeric = numeric.mask(numeric <= 0, np.nan)
    return numeric


def clean_bathrooms(series: pd.Series) -> pd.DataFrame:
    
    text = series.fillna('').astype(str).str.lower()
    
    is_shared = text.str.contains('shared', regex=False)
    
    numeric_str = text.str.extract(r'(\d+\.?\d*)')[0]
    bathrooms = pd.to_numeric(numeric_str, errors='coerce')
    
    half_bath_mask = text.str.contains('half-bath|half bath', regex=True) & bathrooms.isna()
    bathrooms = bathrooms.mask(half_bath_mask, 0.5)
    
    return pd.DataFrame({
        'bathrooms': bathrooms,
        'is_shared_bath': is_shared.astype(int)
    }, index=series.index)


def clean_amenities(series: pd.Series) -> pd.Series:
  
    def parse_item(item):
        if pd.isna(item) or not item:
            return []
        if isinstance(item, list):
            return item
        try:
            return json.loads(item)
        except (json.JSONDecodeError, TypeError):
            try:
                return ast.literal_eval(item)
            except Exception:
                return []

    return series.apply(parse_item)


def clean_boolean(series: pd.Series) -> pd.Series:
   
    mapping = {'t': 1.0, 'f': 0.0, True: 1.0, False: 0.0}
    return series.map(mapping)


def sanitize_listings_pipeline(df: pd.DataFrame) -> pd.DataFrame:
   
    df = df.copy()
    
    df['price'] = clean_price(df['price'])
    
    if 'bathrooms_text' in df.columns:
        bath_df = clean_bathrooms(df['bathrooms_text'])
        df['bathrooms'] = bath_df['bathrooms']
        df['is_shared_bath'] = bath_df['is_shared_bath']
        
    if 'amenities' in df.columns:
        df['amenities_list'] = clean_amenities(df['amenities'])
        df['amenity_count'] = df['amenities_list'].apply(len)
        
    for bool_col in ['host_is_superhost', 'has_availability', 'instant_bookable']:
        if bool_col in df.columns:
            df[bool_col] = clean_boolean(df[bool_col])
            
    keep_columns = [
        'id', 'name', 'host_id', 'host_is_superhost',
        'neighbourhood_cleansed', 'neighbourhood_group_cleansed',
        'latitude', 'longitude', 'property_type', 'room_type',
        'accommodates', 'bathrooms', 'is_shared_bath', 'bedrooms', 'beds',
        'amenity_count', 'amenities_list', 'price',
        'minimum_nights', 'maximum_nights', 'number_of_reviews',
        'review_scores_rating', 'reviews_per_month'
    ]
    
    existing = [col for col in keep_columns if col in df.columns]
    return df[existing]
