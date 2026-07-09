# ============================================================
# Notebook: 03_Gold_Aggregation
# Purpose : Read clean Silver Delta data, create business
#           aggregations, and write results to Gold Delta layer.
# ============================================================


# ------------------------------------------------------------
# Step 1 - Import Required Libraries
# ------------------------------------------------------------

from pyspark.sql.functions import (
    col,
    count,
    sum,
    avg,
    round,
    current_timestamp
)


# ------------------------------------------------------------
# Step 2 - Define Silver and Gold Paths
# ------------------------------------------------------------

silver_path = "abfss://trade-data@sttradelakedev.dfs.core.windows.net/silver/trades"

gold_path = "abfss://trade-data@sttradelakedev.dfs.core.windows.net/gold/trade_summary"


# ------------------------------------------------------------
# Step 3 - Read Silver Delta Data
# ------------------------------------------------------------

silver_df = (
    spark.read
    .format("delta")
    .load(silver_path)
)

display(silver_df)


# ------------------------------------------------------------
# Step 4 - Create Trade Value Column
# ------------------------------------------------------------
# trade_value = price * quantity

trade_value_df = (
    silver_df
    .withColumn(
        "trade_value",
        col("price") * col("quantity")
    )
)

display(trade_value_df)


# ------------------------------------------------------------
# Step 5 - Create Gold Aggregation by Symbol
# ------------------------------------------------------------
# Business metrics:
# - Total trades
# - Total quantity traded
# - Average trade price
# - Total trade value

gold_summary_df = (
    trade_value_df
    .groupBy("symbol")
    .agg(
        count("trade_id").alias("total_trades"),
        sum("quantity").alias("total_quantity"),
        round(avg("price"), 2).alias("average_price"),
        round(sum("trade_value"), 2).alias("total_trade_value")
    )
    .withColumn(
        "gold_processed_time",
        current_timestamp()
    )
)

display(gold_summary_df)


# ------------------------------------------------------------
# Step 6 - Write Gold Summary to Delta
# ------------------------------------------------------------

(
    gold_summary_df
    .write
    .format("delta")
    .mode("overwrite")
    .save(gold_path)
)


# ------------------------------------------------------------
# Step 7 - Verify Gold Delta Data
# ------------------------------------------------------------

gold_result_df = (
    spark.read
    .format("delta")
    .load(gold_path)
)

display(gold_result_df)