import pandera.pandas as pa
from pandera.pandas import Column, Check, DataFrameSchema

CleanedListingsSchema = DataFrameSchema(
    columns={
        "id": Column(int, unique=True, nullable=False),
        "latitude": Column(
            float,
            Check.in_range(40.4, 41.0, error="Latitude is out of NYC geographic bounds"),
            nullable=False
        ),
        "longitude": Column(
            float,
            Check.in_range(-74.3, -73.6, error="Longitude is out of NYC geographic bounds"),
            nullable=False
        ),
        "price": Column(
            float,
            Check.greater_than(0, error="Price must be strictly positive"),
            nullable=True  # Missing prices will be diagnosed in Milestone 5
        ),
        "accommodates": Column(
            int,
            Check.greater_than(0, error="Accommodates must be >= 1"),
            nullable=False
        ),
        "bathrooms": Column(
            float,
            Check.greater_than_or_equal_to(0, error="Bathrooms cannot be negative"),
            nullable=True
        ),
        "amenity_count": Column(
            int,
            Check.greater_than_or_equal_to(0, error="Amenity count cannot be negative"),
            nullable=False
        ),
        "is_shared_bath": Column(
            int,
            Check.isin([0, 1], error="is_shared_bath must be binary 0 or 1"),
            nullable=False
        ),
        "host_is_superhost": Column(
            float,
            Check.isin([0.0, 1.0], error="Superhost flag must be binary 0/1"),
            nullable=True
        ),
    },
    coerce=True,  
    strict=False  
)
