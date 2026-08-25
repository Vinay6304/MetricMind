# =========================================================
# METRICMIND - CUBE SEMANTIC SCHEMA
# Project 1
# =========================================================

ALLOWED_MEASURES = {
    "sales.count",
    "sales.revenue",
    "sales.cost",
    "sales.profit",
}

ALLOWED_DIMENSIONS = {
    "sales.country",
    "sales.region",
    "sales.product",
    "sales.order_date",
}


def validate_query(measures, dimensions):
    """
    Validate that a query uses only approved
    Cube semantic-layer members.
    """

    invalid_measures = set(measures or []) - ALLOWED_MEASURES
    invalid_dimensions = set(dimensions or []) - ALLOWED_DIMENSIONS

    if invalid_measures:
        raise ValueError(
            f"Invalid measures: {sorted(invalid_measures)}"
        )

    if invalid_dimensions:
        raise ValueError(
            f"Invalid dimensions: {sorted(invalid_dimensions)}"
        )

    return True