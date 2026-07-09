# ============================================================
# Notebook: 01_Bronze_Ingestion
# Purpose : Read real-time trade events from Azure Event Hub
#           and write raw messages into Bronze Delta layer.
# ============================================================


# ------------------------------------------------------------
# Step 1 - Import Required Libraries
# ------------------------------------------------------------

from pyspark.sql.functions import col


# ------------------------------------------------------------
# Step 2 - Event Hub Configuration
# ------------------------------------------------------------
# IMPORTANT:
# Do not commit real connection string to GitHub.
# Replace YOUR_KEY with actual key only while running locally.

event_hub_connection_string = (
    "Endpoint=sb://evh-trading-dev.servicebus.windows.net/;"
    "SharedAccessKeyName=RootManageSharedAccessKey;"
    "SharedAccessKey=YOUR_KEY;"
    "EntityPath=trade-events"
)

eh_conf = {
    "eventhubs.connectionString": sc._jvm.org.apache.spark.eventhubs.EventHubsUtils.encrypt(
        event_hub_connection_string
    )
}


# ------------------------------------------------------------
# Step 3 - Read Stream from Azure Event Hub
# ------------------------------------------------------------

raw_stream_df = (
    spark.readStream
    .format("eventhubs")
    .options(**eh_conf)
    .load()
)


# ------------------------------------------------------------
# Step 4 - Display Incoming Messages for Testing
# ------------------------------------------------------------
# This is only for validation. Stop the display stream after testing.

display(
    raw_stream_df.select(
        col("body").cast("string").alias("message")
    ),
    checkpointLocation="abfss://trade-data@sttradelakedev.dfs.core.windows.net/bronze/checkpoints/display_eventhub_test"
)

//need to run 1 to 4 then 5

# ------------------------------------------------------------
# Step 5 - Define Bronze Paths
# ------------------------------------------------------------

bronze_path = "abfss://trade-data@sttradelakedev.dfs.core.windows.net/bronze/trades"

checkpoint_path = "abfss://trade-data@sttradelakedev.dfs.core.windows.net/bronze/checkpoints/trades"


# ------------------------------------------------------------
# Step 6 - Write Raw Stream to Bronze Delta
# ------------------------------------------------------------

bronze_query = (
    raw_stream_df
    .select(
        col("body").cast("string").alias("raw_message"),
        col("enqueuedTime").alias("eventhub_enqueued_time")
    )
    .writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", checkpoint_path)
    .start(bronze_path)
)


# ------------------------------------------------------------
# Step 7 - Verify Bronze Delta Data
# ------------------------------------------------------------

display(
    spark.read
    .format("delta")
    .load(bronze_path)
)


# ------------------------------------------------------------
# Step 8 - Stop Streaming Query After Testing
# ------------------------------------------------------------
# Run this after verification to avoid continuous cluster usage.

bronze_query.stop()