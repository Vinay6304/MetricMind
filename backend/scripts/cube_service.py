import json
import requests

from .cube_schema import validate_query


CUBE_API_URL = "http://localhost:4000/cubejs-api/v1/load"


def run_cube_query(measures=None, dimensions=None, filters=None):
    """
    Execute a validated query against the Cube semantic layer.
    """

    measures = measures or []
    dimensions = dimensions or []
    filters = filters or []

    # Validate semantic-layer members
    validate_query(
        measures=measures,
        dimensions=dimensions
    )

    query = {
        "measures": measures,
        "dimensions": dimensions,
        "filters": filters
    }

    response = requests.get(
        CUBE_API_URL,
        params={
            "query": json.dumps(query)
        },
        timeout=30
    )

    response.raise_for_status()

    return response.json()