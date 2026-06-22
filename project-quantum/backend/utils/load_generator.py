import urllib.request
import json
import random
import time
import sys

BASE_URL = "http://localhost:8000"

print("==================================================")
print("🚀 Quantum Enterprise AI Load Generator Initialized")
print(f"Target backend: {BASE_URL}")
print("Generating steady traffic to populate Grafana charts...")
print("Press Ctrl+C to stop the load generator.")
print("==================================================\n")

models_traffic = [
    {
        "endpoint": "/predict/loan",
        "payload_fn": lambda: {
            "income": random.randint(30000, 150000),
            "credit_score": random.randint(580, 830),
            "loan_amount": random.randint(50000, 400000)
        }
    },
    {
        "endpoint": "/predict/house",
        "payload_fn": lambda: {
            "area": random.randint(800, 4500),
            "bedrooms": random.randint(1, 5),
            "bathrooms": float(random.randint(1, 4))
        }
    },
    {
        "endpoint": "/predict/churn",
        "payload_fn": lambda: {
            "tenure": random.randint(1, 72),
            "monthly_charges": random.randint(20, 120),
            "contract_type": random.randint(0, 2)
        }
    }
]

request_count = 0

try:
    while True:
        # Choose a random prediction endpoint
        target = random.choice(models_traffic)
        url = f"{BASE_URL}{target['endpoint']}"
        payload = target["payload_fn"]()
        
        headers = {"Content-Type": "application/json"}
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode("utf-8"), 
            headers=headers, 
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                response.read()
        except Exception as e:
            # Silence connection errors to keep terminal clean if server drops
            pass
            
        request_count += 1
        
        # Every 75 requests, inject a chaos spike to make the metrics graphs look realistic & dynamic
        if request_count % 75 == 0:
            chaos_type = random.choice(["latency", "error"])
            if chaos_type == "latency":
                print("⚡ [Chaos Engine] Simulating Latency Spike...")
                chaos_url = f"{BASE_URL}/simulate/high-latency"
            else:
                print("💥 [Chaos Engine] Simulating HTTP 500 Server Error...")
                chaos_url = f"{BASE_URL}/simulate/error"
                
            req_chaos = urllib.request.Request(chaos_url, method="POST")
            try:
                # Set a small timeout so the load generator doesn't block forever on high-latency simulations
                with urllib.request.urlopen(req_chaos, timeout=6) as resp:
                    resp.read()
            except Exception:
                pass
        
        # Display progress every 20 requests
        if request_count % 20 == 0:
            print(f"📈 Dispatched {request_count} prediction inference payloads successfully.")
            
        # Steady random sleep to keep CPU usage low while sending a continuous stream of metrics
        time.sleep(random.uniform(0.1, 0.4))

except KeyboardInterrupt:
    print("\n🏁 Load generator terminated. Check Grafana to see the updated metrics charts!")
    sys.exit(0)
