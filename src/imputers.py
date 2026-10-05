import numpy as np
import pandas as pd


def add_missing_indicators(df, columns):
    df = df.copy()
    for col in columns:
        if col in df.columns:
            df[f'{col}_missing'] = df[col].isna().astype(int)
    return df


def impute_structural_features(df):
    df = df.copy()
    group_cols = ['room_type', 'accommodates']

    for col in ['bedrooms', 'beds', 'bathrooms']:
        if col in df.columns:
            median_by_group = df.groupby(group_cols)[col].transform('median')
            df[col] = df[col].fillna(median_by_group)
            df[col] = df[col].fillna(df[col].median()).fillna(1.0)
    return df


def impute_review_features(df):
    df = df.copy()
    if 'reviews_per_month' in df.columns:
        df['reviews_per_month'] = df['reviews_per_month'].fillna(0.0)
    if 'review_scores_rating' in df.columns:
        median_rating = df['review_scores_rating'].median()
        df['review_scores_rating'] = df['review_scores_rating'].fillna(median_rating)
    if 'host_is_superhost' in df.columns:
        df['host_is_superhost'] = df['host_is_superhost'].fillna(0.0)
    return df


def run_imputation_pipeline(df):
    indicator_cols = ['bedrooms', 'beds', 'bathrooms', 'review_scores_rating']
    df = add_missing_indicators(df, indicator_cols)
    df = impute_structural_features(df)
    df = impute_review_features(df)
    return df
