import os

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from scripts.analytics import (
    get_dashboard_data,
    get_cube_dashboard_data
)

from scripts.ai_service import ask_ai


app = Flask(__name__)
CORS(app)


# =========================================================
# DASHBOARD API
# =========================================================

@app.route("/api/dashboard")
def dashboard():

    region = request.args.get("region")

    data = get_dashboard_data(
        region=region
    )

    return jsonify(data)


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return "MetricMind API is running!"


# =========================================================
# DASHBOARD PAGE
# =========================================================

@app.route("/dashboard")
def dashboard_page():

    return send_from_directory(
        os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__)
                )
            ),
            "frontend"
        ),
        "index.html"
    )


# =========================================================
# CUBE API
# =========================================================

@app.route("/api/cube-dashboard")
def cube_dashboard():

    data = get_cube_dashboard_data()

    return jsonify(data)


# =========================================================
# AI QUESTION API
# =========================================================

@app.route(
    "/api/ai",
    methods=["POST"]
)
def ai_query():

    body = request.get_json(
        silent=True
    ) or {}

    prompt = body.get(
        "prompt",
        ""
    ).strip()


    if not prompt:

        return jsonify({
            "success": False,
            "error": "Prompt is required"
        }), 400


    try:

        # -------------------------------------------------
        # Get LIVE dashboard data
        # -------------------------------------------------

        dashboard_data = get_dashboard_data()


        # -------------------------------------------------
        # Ask MetricMind
        # -------------------------------------------------

        result = ask_ai(
            prompt,
            dashboard_data
        )


        return jsonify({
            "success": True,
            "response": result
        })


    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================================================
# AI AUTOMATIC SUMMARY
# =========================================================

@app.route(
    "/api/ai/summary",
    methods=["GET"]
)
def ai_summary():

    try:

        # -------------------------------------------------
        # Get LIVE dashboard data
        # -------------------------------------------------

        dashboard_data = get_dashboard_data()


        # -------------------------------------------------
        # Extract data
        # -------------------------------------------------

        overall = dashboard_data.get(
            "overall"
        )

        countries = dashboard_data.get(
            "countries",
            []
        )

        products = dashboard_data.get(
            "products",
            []
        )

        regions = dashboard_data.get(
            "regions",
            []
        )

        months = dashboard_data.get(
            "months",
            []
        )


        # -------------------------------------------------
        # SAFETY CHECK
        # -------------------------------------------------

        if not overall:

            return jsonify({
                "success": False,
                "error": "Dashboard data is unavailable"
            }), 500


        # -------------------------------------------------
        # TOP COUNTRY
        # -------------------------------------------------

        top_country = (
            max(
                countries,
                key=lambda row: float(row[2])
            )
            if countries
            else None
        )


        # -------------------------------------------------
        # TOP PRODUCT BY REVENUE
        # -------------------------------------------------

        top_product = (
            max(
                products,
                key=lambda row: float(row[2])
            )
            if products
            else None
        )


        # -------------------------------------------------
        # TOP PRODUCT BY PROFIT
        # -------------------------------------------------

        top_profit_product = (
            max(
                products,
                key=lambda row: float(row[4])
            )
            if products
            else None
        )


        # -------------------------------------------------
        # TOP REGION
        # -------------------------------------------------

        top_region = (
            max(
                regions,
                key=lambda row: float(row[2])
            )
            if regions
            else None
        )


        # -------------------------------------------------
        # BEST MONTH
        # -------------------------------------------------

        best_month = (
            max(
                months,
                key=lambda row: float(row[2])
            )
            if months
            else None
        )


        # -------------------------------------------------
        # LOWEST MONTH
        # -------------------------------------------------

        weakest_month = (
            min(
                months,
                key=lambda row: float(row[2])
            )
            if months
            else None
        )


        # -------------------------------------------------
        # RETURN SUMMARY
        # -------------------------------------------------

        return jsonify({

            "success": True,

            "summary": {

                "total_orders": overall[0],

                "total_revenue": overall[1],

                "total_cost": overall[2],

                "total_profit": overall[3],

                "profit_margin": overall[4],

                "top_country": (
                    {
                        "name": top_country[0],
                        "orders": top_country[1],
                        "revenue": top_country[2],
                        "cost": top_country[3],
                        "profit": top_country[4]
                    }
                    if top_country
                    else None
                ),

                "top_product": (
                    {
                        "name": top_product[0],
                        "orders": top_product[1],
                        "revenue": top_product[2],
                        "cost": top_product[3],
                        "profit": top_product[4]
                    }
                    if top_product
                    else None
                ),

                "top_profit_product": (
                    {
                        "name": top_profit_product[0],
                        "orders": top_profit_product[1],
                        "revenue": top_profit_product[2],
                        "cost": top_profit_product[3],
                        "profit": top_profit_product[4]
                    }
                    if top_profit_product
                    else None
                ),

                "top_region": (
                    {
                        "name": top_region[0],
                        "orders": top_region[1],
                        "revenue": top_region[2],
                        "cost": top_region[3],
                        "profit": top_region[4]
                    }
                    if top_region
                    else None
                ),

                "best_month": (
                    {
                        "month": best_month[0],
                        "orders": best_month[1],
                        "revenue": best_month[2],
                        "cost": best_month[3],
                        "profit": best_month[4]
                    }
                    if best_month
                    else None
                ),

                "weakest_month": (
                    {
                        "month": weakest_month[0],
                        "orders": weakest_month[1],
                        "revenue": weakest_month[2],
                        "cost": weakest_month[3],
                        "profit": weakest_month[4]
                    }
                    if weakest_month
                    else None
                )
            }

        })


    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )