# ─────────────────────────────────────────────
# PART 1 — Import Libraries
# ─────────────────────────────────────────────
import json
import random
import time
from datetime import datetime
from azure.eventhub import EventHubProducerClient, EventData
from config import CONNECTION_STRING, EVENT_HUB_NAME




# ─────────────────────────────────────────────
# PART 2 — Generate One Random Trade
# ─────────────────────────────────────────────
def generate_trade():
    
    symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", 
               "TSLA", "INFY", "TCS", "WIPRO"]
    
    trade = {
        "trade_id"   : f"T{random.randint(100000, 999999)}",
        "symbol"     : random.choice(symbols),
        "quantity"   : random.randint(1, 1000),
        "price"      : round(random.uniform(100, 5000), 2),
        "trade_time" : datetime.utcnow().isoformat(),
        "trader_id"  : f"TR{random.randint(1, 50)}",
        "status"     : "RAW"
    }
    
    return trade


# ─────────────────────────────────────────────
# PART 3 — Send Trades to Event Hub
# ─────────────────────────────────────────────
def send_trades():
    
    # Connect to Event Hub
    producer = EventHubProducerClient.from_connection_string(
        conn_str      = CONNECTION_STRING,
        eventhub_name = EVENT_HUB_NAME
    )
    
    print("🚀 Trade Generator Started!")
    print("   Press Ctrl+C to stop")
    print("─" * 50)
    
    batch_number = 0
    
    with producer:
        
        while True:
            
            # Step A — Create empty batch
            event_data_batch = producer.create_batch()
            
            # Step B — Generate 10 trades and add to batch
            for _ in range(10):
                
                # Generate one trade
                trade = generate_trade()
                
                # Convert trade to JSON text
                trade_json = json.dumps(trade)
                
                # Wrap in EventData and add to batch
                event_data_batch.add(EventData(trade_json))
            
            # Step C — Send batch to Event Hub
            producer.send_batch(event_data_batch)
            
            # Step D — Count and print
            batch_number += 1
            print(f"✅ Batch {batch_number} sent → 10 trades")
            print(f"   Trade sample : {trade['trade_id']} | "
                  f"{trade['symbol']} | "
                  f"Qty: {trade['quantity']} | "
                  f"Price: ${trade['price']}")
            print(f"   Time         : {datetime.utcnow().isoformat()}")
            print("─" * 50)
            
            # Step E — Wait 2 seconds
            time.sleep(2)


# ─────────────────────────────────────────────
# PART 4 — Run the Script
# ─────────────────────────────────────────────
if __name__ == "__main__":
    send_trades()