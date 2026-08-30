import os
import re
from datetime import datetime
from decimal import Decimal

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

AI_MODE = os.getenv(
    "METRICMIND_AI_MODE",
    "mock"
).lower()


# =========================================================
# OPENAI MODEL
# =========================================================

llm = None

if AI_MODE == "openai":
    llm = ChatOpenAI(
        model="gpt-5-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0
    )


# =========================================================
# FORMAT HELPERS
# =========================================================

def numeric_value(value):
    """Convert Decimal/string/numeric values to float."""

    if value is None:
        return 0.0

    if isinstance(value, Decimal):
        return float(value)

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def format_number(value):
    """Format a normal number."""

    number = numeric_value(value)

    if number.is_integer():
        return f"{int(number):,}"

    return f"{number:,.2f}"


def format_money(value):
    """Format currency consistently with the dashboard."""

    return f"₹{format_number(value)}"

def format_date(value):
    """Format dashboard dates for readable AI responses."""

    if value is None:
        return "Unknown date"

    if isinstance(value, datetime):
        return value.strftime("%b %d, %Y")

    try:
        parsed = datetime.fromisoformat(
            str(value)
        )
        return parsed.strftime("%b %d, %Y")

    except (TypeError, ValueError):
        return str(value)


# =========================================================
# DATA ACCESS
# =========================================================

def get_rows(dashboard_data, category):
    """Safely retrieve a dashboard data section."""

    rows = dashboard_data.get(category, [])

    if not rows:
        return []

    return rows


# =========================================================
# METRIC DETECTION
# =========================================================

def detect_metric(prompt):
    """
    Determine which business metric the user is asking about.

    Priority:
    1. Profit
    2. Cost
    3. Orders
    4. Revenue / Sales
    """

    text = prompt.lower()

    if any(word in text for word in [
        "profit margin",
        "margin"
    ]):
        return "margin"

    if any(word in text for word in [
        "profit",
        "profitable",
        "earnings",
        "earn"
    ]):
        return "profit"

    if any(word in text for word in [
        "cost",
        "expense",
        "expenses"
    ]):
        return "cost"

    if any(word in text for word in [
        "order",
        "orders",
        "number of orders",
        "most orders",
        "fewest orders"
    ]):
        return "orders"

    if any(word in text for word in [
        "sales",
        "sale",
        "revenue",
        "income",
        "turnover"
    ]):
        return "revenue"

    # Default business metric
    return "revenue"


# =========================================================
# DIRECTION DETECTION
# =========================================================

def detect_direction(prompt):
    """
    Determine whether the user wants highest,
    lowest, or a general result.
    """

    text = prompt.lower()

    if any(word in text for word in [
        "lowest",
        "least",
        "smallest",
        "minimum",
        "weakest",
        "worst"
    ]):
        return "lowest"

    if any(word in text for word in [
        "highest",
        "top",
        "most",
        "largest",
        "maximum",
        "best",
        "strongest"
    ]):
        return "highest"

    return "highest"


# =========================================================
# METRIC VALUE
# =========================================================

def get_metric_value(row, metric):
    """
    Dashboard tuple structure:

    [0] Name
    [1] Orders
    [2] Revenue
    [3] Cost
    [4] Profit
    """

    if metric == "orders":
        return numeric_value(row[1])

    if metric == "revenue":
        return numeric_value(row[2])

    if metric == "cost":
        return numeric_value(row[3])

    if metric == "profit":
        return numeric_value(row[4])

    return numeric_value(row[2])


def metric_label(metric):
    labels = {
        "orders": "orders",
        "revenue": "sales revenue",
        "cost": "cost",
        "profit": "profit",
        "margin": "profit margin"
    }

    return labels.get(metric, "sales revenue")


# =========================================================
# CATEGORY DETECTION
# =========================================================

def detect_category(prompt):
    """
    Identify the dimension being discussed.
    """

    text = prompt.lower()

    if any(word in text for word in [
        "country",
        "countries",
        "nation"
    ]):
        return "countries"

    if any(word in text for word in [
        "product",
        "products",
        "item",
        "items"
    ]):
        return "products"

    if any(word in text for word in [
        "region",
        "regions"
    ]):
        return "regions"

    if any(word in text for word in [
        "month",
        "monthly",
        "months",
        "period"
    ]):
        return "months"

    return None


# =========================================================
# OVERALL INSIGHT
# =========================================================

def overall_sales_insight(dashboard_data):

    overall = dashboard_data.get("overall")

    if not overall:
        return (
            "MetricMind Insight:\n"
            "Overall sales data is not available."
        )

    total_orders = overall[0]
    total_revenue = overall[1]
    total_cost = overall[2]
    total_profit = overall[3]
    profit_margin = overall[4]

    return (
        "MetricMind Insight:\n"
        f"Total sales revenue is {format_money(total_revenue)} "
        f"from {format_number(total_orders)} orders. "
        f"Total cost is {format_money(total_cost)}, "
        f"total profit is {format_money(total_profit)}, "
        f"and the profit margin is {format_number(profit_margin)}%."
    )


# =========================================================
# CATEGORY INSIGHT
# =========================================================

def category_insight(dashboard_data, category, metric, direction):

    rows = get_rows(
        dashboard_data,
        category
    )

    if not rows:
        return (
            "MetricMind Insight:\n"
            f"No {category} data is available."
        )

    # -----------------------------------------------------
    # Margin is calculated from revenue and profit
    # -----------------------------------------------------

    if metric == "margin":

        valid_rows = []

        for row in rows:

            revenue = numeric_value(row[2])
            profit = numeric_value(row[4])

            margin = (
                (profit / revenue) * 100
                if revenue != 0
                else 0
            )

            valid_rows.append(
                (row, margin)
            )

        if direction == "lowest":
            selected = min(
                valid_rows,
                key=lambda item: item[1]
            )
        else:
            selected = max(
                valid_rows,
                key=lambda item: item[1]
            )

        row = selected[0]
        value = selected[1]

        return (
            "MetricMind Insight:\n"
            f"{row[0]} has the {direction} profit margin at "
            f"{format_number(value)}%, with revenue of "
            f"{format_money(row[2])} and profit of "
            f"{format_money(row[4])}."
        )

    # -----------------------------------------------------
    # Normal metrics
    # -----------------------------------------------------

    if direction == "lowest":

        selected = min(
            rows,
            key=lambda row: get_metric_value(row, metric)
        )

    else:

        selected = max(
            rows,
            key=lambda row: get_metric_value(row, metric)
        )

    value = get_metric_value(
        selected,
        metric
    )

    label = metric_label(metric)

    if metric == "orders":

        value_text = format_number(value)

    else:

        value_text = format_money(value)

    return (
        "MetricMind Insight:\n"
        f"{selected[0]} has the {direction} {label} at "
        f"{value_text}. "
        f"Revenue is {format_money(selected[2])}, "
        f"cost is {format_money(selected[3])}, "
        f"and profit is {format_money(selected[4])}."
    )


# =========================================================
# RANKING INSIGHT
# =========================================================

def ranking_insight(
    dashboard_data,
    category,
    metric
):

    rows = get_rows(
        dashboard_data,
        category
    )

    if not rows:
        return (
            "MetricMind Insight:\n"
            f"No {category} data is available."
        )

    if metric == "margin":

        ranking = []

        for row in rows:

            revenue = numeric_value(row[2])
            profit = numeric_value(row[4])

            margin = (
                (profit / revenue) * 100
                if revenue != 0
                else 0
            )

            ranking.append(
                (row, margin)
            )

        ranking.sort(
            key=lambda item: item[1],
            reverse=True
        )

    else:

        ranking = sorted(
            rows,
            key=lambda row: get_metric_value(
                row,
                metric
            ),
            reverse=True
        )

    label = metric_label(metric)

    result = (
        "MetricMind Insight:\n"
        f"{category.title()} ranked by {label}:"
    )

    for index, item in enumerate(
        ranking,
        start=1
    ):

        if metric == "margin":

            row = item[0]
            value = item[1]

            value_text = (
                f"{format_number(value)}%"
            )

        else:

            row = item
            value = get_metric_value(
                row,
                metric
            )

            if metric == "orders":

                value_text = format_number(value)

            else:

                value_text = format_money(value)

        result += (
            f"\n{index}. {row[0]} — "
            f"{value_text}"
        )

    return result


# =========================================================
# COMPARISON DETECTION
# =========================================================

def find_named_entities(
    prompt,
    rows
):
    """
    Find dashboard entity names mentioned in the question.
    """

    text = prompt.lower()

    matches = []

    for row in rows:

        name = str(row[0])

        if name.lower() in text:

            matches.append(row)

    return matches

def is_comparison_request(prompt):
    """Check whether the user is explicitly asking for a comparison."""

    text = prompt.lower()

    return any(phrase in text for phrase in [
        "compare",
        "comparison",
        "versus",
        "vs",
        "difference between",
        "more than",
        "less than",
        "higher than",
        "lower than",
        "better than",
        "worse than",
        "more profitable than",
        "less profitable than"
    ])

# =========================================================
# COMPARISON INSIGHT
# =========================================================

def comparison_insight(
    dashboard_data,
    category,
    metric,
    prompt
):

    rows = get_rows(
        dashboard_data,
        category
    )

    matches = find_named_entities(
        prompt,
        rows
    )

    if len(matches) < 2:

        return None

    first = matches[0]
    second = matches[1]

    first_value = get_metric_value(
        first,
        metric
    )

    second_value = get_metric_value(
        second,
        metric
    )

    difference = abs(
        first_value - second_value
    )

    label = metric_label(metric)

    if first_value > second_value:

        winner = first
        loser = second

    elif second_value > first_value:

        winner = second
        loser = first

    else:

        return (
            "MetricMind Insight:\n"
            f"{first[0]} and {second[0]} have the same "
            f"{label}."
        )

    if metric == "orders":

        first_text = format_number(first_value)
        second_text = format_number(second_value)
        difference_text = format_number(difference)

    else:

        first_text = format_money(first_value)
        second_text = format_money(second_value)
        difference_text = format_money(difference)

    return (
        "MetricMind Insight:\n"
        f"{winner[0]} has higher {label} than "
        f"{loser[0]}. "
        f"{first[0]}: {first_text}; "
        f"{second[0]}: {second_text}. "
        f"The difference is {difference_text}."
    )


# =========================================================
# MONTHLY INSIGHT
# =========================================================

def monthly_insight(
    dashboard_data,
    metric
):

    months = get_rows(
        dashboard_data,
        "months"
    )

    if not months:

        return (
            "MetricMind Insight:\n"
            "No monthly sales data is available."
        )

    highest = max(
        months,
        key=lambda row: get_metric_value(
            row,
            metric
        )
    )

    lowest = min(
        months,
        key=lambda row: get_metric_value(
            row,
            metric
        )
    )

    label = metric_label(metric)

    high_value = get_metric_value(
        highest,
        metric
    )

    low_value = get_metric_value(
        lowest,
        metric
    )

    if metric == "orders":

        high_text = format_number(high_value)
        low_text = format_number(low_value)

    else:

        high_text = format_money(high_value)
        low_text = format_money(low_value)

    highest_date = format_date(highest[0])
    lowest_date = format_date(lowest[0])

    return (
        "MetricMind Insight:\n"
        f"The strongest {label} period was "
        f"{highest_date}, with {high_text}. "
        f"The weakest {label} period was "
        f"{lowest_date}, with {low_text}."
    )

# =========================================================
# TREND INSIGHT
# =========================================================

def trend_insight(
    dashboard_data,
    metric
):
    """
    Analyze whether a metric is increasing,
    decreasing, or unchanged over time.
    """

    months = get_rows(
        dashboard_data,
        "months"
    )

    if not months:

        return (
            "MetricMind Insight:\n"
            "No monthly sales data is available."
        )

    if len(months) < 2:

        return (
            "MetricMind Insight:\n"
            "Not enough monthly data is available "
            "to determine a trend."
        )

    first_month = months[0]
    last_month = months[-1]

    first_value = get_metric_value(
        first_month,
        metric
    )

    last_value = get_metric_value(
        last_month,
        metric
    )

    difference = last_value - first_value

    label = metric_label(metric)

    if difference > 0:

        direction = "increasing"

    elif difference < 0:

        direction = "decreasing"

    else:

        direction = "unchanged"

    if metric == "orders":

        first_text = format_number(first_value)
        last_text = format_number(last_value)
        difference_text = format_number(
            abs(difference)
        )

    else:

        first_text = format_money(first_value)
        last_text = format_money(last_value)
        difference_text = format_money(
            abs(difference)
        )

    return (
        "MetricMind Insight:\n"
        f"{label.title()} is {direction} over time. "
        f"It changed from {first_text} in "
        f"{first_month[0]} to {last_text} in "
        f"{last_month[0]}. "
        f"The overall change is {difference_text}."
    )

# =========================================================
# OPENAI DATA CONTEXT
# =========================================================

def build_data_context(dashboard_data):

    lines = []

    overall = dashboard_data.get(
        "overall"
    )

    if overall:

        lines.append("OVERALL SALES")
        lines.append(
            f"Total Orders: {format_number(overall[0])}"
        )
        lines.append(
            f"Total Revenue: {format_money(overall[1])}"
        )
        lines.append(
            f"Total Cost: {format_money(overall[2])}"
        )
        lines.append(
            f"Total Profit: {format_money(overall[3])}"
        )
        lines.append(
            f"Profit Margin: {format_number(overall[4])}%"
        )

    # -----------------------------------------------------
    # COUNTRIES
    # -----------------------------------------------------

    lines.append("\nCOUNTRIES")

    for row in dashboard_data.get(
        "countries",
        []
    ):

        lines.append(
            f"{row[0]} | "
            f"Orders: {format_number(row[1])} | "
            f"Revenue: {format_money(row[2])} | "
            f"Cost: {format_money(row[3])} | "
            f"Profit: {format_money(row[4])}"
        )

    # -----------------------------------------------------
    # PRODUCTS
    # -----------------------------------------------------

    lines.append("\nPRODUCTS")

    for row in dashboard_data.get(
        "products",
        []
    ):

        lines.append(
            f"{row[0]} | "
            f"Orders: {format_number(row[1])} | "
            f"Revenue: {format_money(row[2])} | "
            f"Cost: {format_money(row[3])} | "
            f"Profit: {format_money(row[4])}"
        )

    # -----------------------------------------------------
    # REGIONS
    # -----------------------------------------------------

    lines.append("\nREGIONS")

    for row in dashboard_data.get(
        "regions",
        []
    ):

        lines.append(
            f"{row[0]} | "
            f"Orders: {format_number(row[1])} | "
            f"Revenue: {format_money(row[2])} | "
            f"Cost: {format_money(row[3])} | "
            f"Profit: {format_money(row[4])}"
        )

    # -----------------------------------------------------
    # MONTHS
    # -----------------------------------------------------

    lines.append("\nMONTHS")

    for row in dashboard_data.get(
        "months",
        []
    ):

        lines.append(
            f"{row[0]} | "
            f"Orders: {format_number(row[1])} | "
            f"Revenue: {format_money(row[2])} | "
            f"Cost: {format_money(row[3])} | "
            f"Profit: {format_money(row[4])}"
        )

    return "\n".join(lines)


# =========================================================
# OPENAI RESPONSE
# =========================================================

def openai_response(
    prompt,
    dashboard_data
):

    if llm is None:

        return (
            "MetricMind Insight:\n"
            "OpenAI model is not configured."
        )

    data_context = build_data_context(
        dashboard_data
    )

    full_prompt = f"""
You are MetricMind, a professional sales analytics assistant.

Analyze ONLY the provided sales data.

Never invent values.
Never assume values that are not present.
Use exact numerical values from the dataset.

Currency:
All monetary values are in Indian Rupees (₹).

SALES DATA
==========

{data_context}

USER QUESTION
=============

{prompt}

RESPONSE RULES
==============

1. Answer the question directly.
2. Use actual numbers.
3. Distinguish revenue, cost, profit, orders and profit margin.
4. If the user asks for highest, find the actual maximum.
5. If the user asks for lowest, find the actual minimum.
6. If the user asks for a comparison, calculate the difference.
7. Keep the answer concise.
8. Do not claim information that is absent from the dataset.

Start with:

MetricMind Insight:
"""

    response = llm.invoke(
        full_prompt
    )

    return response.content


# =========================================================
# MOCK AI
# =========================================================

def mock_response(
    prompt,
    dashboard_data
):

    metric = detect_metric(prompt)

    category = detect_category(prompt)

    direction = detect_direction(prompt)

    text = prompt.lower()

    # -----------------------------------------------------
    # DETECT CATEGORY FROM NAMED DASHBOARD ENTITIES
    # -----------------------------------------------------

    if category is None:

        for possible_category in [
            "countries",
            "products",
            "regions",
            "months"
        ]:

            rows = get_rows(
                dashboard_data,
                possible_category
            )

            matches = find_named_entities(
                prompt,
                rows
            )

            if matches:

                category = possible_category
                break

    # -----------------------------------------------------
    # TREND ANALYSIS
    # -----------------------------------------------------

    if any(word in text for word in [
        "increasing",
        "decreasing",
        "improving",
        "declining",
        "trend",
        "over time"
    ]):

        return trend_insight(
            dashboard_data,
            metric
        )

    # -----------------------------------------------------
    # COMPARISON
    # -----------------------------------------------------

    comparison_phrases = [
        "compare",
        "comparison",
        "versus",
        "vs",
        "difference between",
        "more than",
        "less than",
        "higher than",
        "lower than",
        "better than",
        "worse than",
        "more profitable than",
        "less profitable than"
    ]

    is_comparison = (
        is_comparison_request(prompt)
        or any(
            phrase in text
            for phrase in comparison_phrases
        )
    )

    if is_comparison:

        if category:

            comparison = comparison_insight(
                dashboard_data,
                category,
                metric,
                prompt
            )

            if comparison:

                return comparison

        return (
            "MetricMind Insight:\n"
            "Unable to complete the requested comparison."
        )

    # -----------------------------------------------------
    # OVERALL
    # -----------------------------------------------------

    if (
        category is None
        and any(word in text for word in [
            "overall",
            "total",
            "business performance",
            "sales performance",
            "summary"
        ])
    ):

        return overall_sales_insight(
            dashboard_data
        )

    # -----------------------------------------------------
    # MONTHLY
    # -----------------------------------------------------

    if category == "months":

        return monthly_insight(
            dashboard_data,
            metric
        )

    # -----------------------------------------------------
    # RANKING REQUEST
    # -----------------------------------------------------

    if category and any(word in text for word in [
        "rank",
        "ranking",
        "list",
        "top",
        "all"
    ]):

        return ranking_insight(
            dashboard_data,
            category,
            metric
        )

    # -----------------------------------------------------
    # HIGHEST / LOWEST
    # -----------------------------------------------------

    if category:

        return category_insight(
            dashboard_data,
            category,
            metric,
            direction
        )

    # -----------------------------------------------------
    # GENERAL SALES QUESTION
    # -----------------------------------------------------

    if any(word in text for word in [
        "sales",
        "revenue",
        "profit",
        "cost",
        "orders"
    ]):

        return overall_sales_insight(
            dashboard_data
        )
    
# -----------------------------------------------------
    # DEFAULT
    # -----------------------------------------------------

    return (
        "MetricMind Insight:\n"
        "I can analyze sales data by country, "
        "product, region and month, including "
        "revenue, cost, profit and orders."
    )

# =========================================================
# Main AI FUNCTION
# =========================================================

def ask_ai(
    prompt,
    dashboard_data
):

    if AI_MODE == "mock":
    
        return mock_response(
            prompt,
            dashboard_data
        )

    if AI_MODE == "openai":

        return openai_response(
            prompt,
            dashboard_data
        )

    return (
        f"Invalid METRICMIND_AI_MODE: {AI_MODE}"
    )