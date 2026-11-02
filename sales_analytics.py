"""
Retail Sales Performance & Profit Margin Analytics Engine
Author: Aaryan Tulsankar (GitHub: @TulsankarAaryan)

Description:
    End-to-end SQL & Python analytical pipeline executing in-memory on SQLite.
    Computes sub-category level gross profit margins, generates profitability-weighted
    revenue visualizations, and dynamically classifies product tiers using SQL CASE statements.
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def get_connection():
    """Initializes and returns an in-memory SQLite connection."""
    return sqlite3.connect(":memory:")


def load_sales_data(conn: sqlite3.Connection) -> pd.DataFrame:
    """Populates raw transactional records into the in-memory SQLite database."""
    dataset = {
        "Order_ID": [1, 2, 3, 4, 5, 6],
        "Category": ["Tech", "Tech", "Furniture", "Furniture", "Office", "Office"],
        "Sub_Category": ["Phones", "Laptops", "Chairs", "Tables", "Paper", "Pens"],
        "Sales": [1000, 2000, 1500, 1200, 500, 300],
        "Profit": [100, 250, -50, -100, 10, 5],
    }
    df = pd.DataFrame(dataset)
    df.to_sql("Sales_Data", conn, index=False, if_exists="replace")
    print("✓ Successfully loaded sales dataset into SQLite in-memory store.")
    return df


def analyze_margins(conn: sqlite3.Connection) -> pd.DataFrame:
    """Executes SQL aggregation to calculate total sales, profit, and margin percentage per sub-category."""
    query = """
    SELECT
        Category,
        Sub_Category,
        SUM(Sales) AS Total_Sales,
        SUM(Profit) AS Total_Profit,
        ROUND((CAST(SUM(Profit) AS FLOAT) / SUM(Sales)) * 100, 2) AS Margin_Percentage
    FROM Sales_Data
    GROUP BY Category, Sub_Category
    ORDER BY Margin_Percentage DESC;
    """
    df = pd.read_sql(query, conn)
    return df


def generate_performance_tiers(conn: sqlite3.Connection) -> pd.DataFrame:
    """Applies nested SQL subqueries and conditional CASE statements to classify operational tiers."""
    query = """
    SELECT
        Sub_Category,
        Total_Sales,
        Total_Profit,
        Margin_Percentage,
        CASE
            WHEN Margin_Percentage > 10 THEN 'High Performer'
            WHEN Margin_Percentage BETWEEN 0 AND 10 THEN 'Stable'
            ELSE 'Review Required'
        END AS Performance_Status
    FROM (
        SELECT
            Sub_Category,
            SUM(Sales) AS Total_Sales,
            SUM(Profit) AS Total_Profit,
            ROUND((CAST(SUM(Profit) AS FLOAT) / SUM(Sales)) * 100, 2) AS Margin_Percentage
        FROM Sales_Data
        GROUP BY Sub_Category
    )
    ORDER BY Total_Sales DESC;
    """
    df = pd.read_sql(query, conn)
    return df


def plot_sales_and_margins(df: pd.DataFrame, output_path: str = "sales_performance_report.png"):
    """Renders and saves a color-coded Seaborn bar visualization of sales and profitability."""
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))

    palette = sns.color_palette("RdYlGn", n_colors=len(df))
    ax = sns.barplot(
        data=df,
        x="Sub_Category",
        y="Total_Sales",
        palette=palette,
        hue="Sub_Category",
        legend=False,
    )

    plt.title("Sales Revenue by Sub-Category (Profitability Heatmap)", fontsize=14, weight="bold", pad=15)
    plt.xlabel("Product Sub-Category", fontsize=11, labelpad=10)
    plt.ylabel("Total Revenue ($)", fontsize=11, labelpad=10)

    # Annotate margin percentages on top of bars
    for idx, row in df.iterrows():
        margin = row["Margin_Percentage"]
        symbol = "+" if margin >= 0 else ""
        ax.text(
            idx,
            row["Total_Sales"] + 40,
            f"{symbol}{margin:.1f}%",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    plt.ylim(0, df["Total_Sales"].max() * 1.15)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"✓ Saved analytics chart to {output_path}")
    plt.close()


def main():
    print("=" * 60)
    print("  Retail Sales & Profitability Analytics Engine")
    print("  Author: Aaryan Tulsankar | GitHub: @TulsankarAaryan")
    print("=" * 60)

    conn = get_connection()
    load_sales_data(conn)

    print("\n--- Sub-Category Profit Margin Analysis ---")
    margin_df = analyze_margins(conn)
    print(margin_df.to_string(index=False))

    plot_sales_and_margins(margin_df)

    print("\n--- Operational Tier Classification Report ---")
    tier_df = generate_performance_tiers(conn)
    print(tier_df.to_string(index=False))
    print("\n✓ Pipeline execution complete.")


if __name__ == "__main__":
    main()
