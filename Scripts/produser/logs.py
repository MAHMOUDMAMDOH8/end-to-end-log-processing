import json
import random
import time
from datetime import datetime, timedelta

class LogGenerator:
    def __init__(self):
        # Sample data stores
        self.users = [{"user_id": f"user_{i}", "name": f"User {i}"} for i in range(1, 1001)]
        self.products = [
            {"product_id": f"prod_{i:05d}", "name": f"Product {i}", "category": random.choice(["Electronics", "Clothing", "Home", "Books"]), "price": round(random.uniform(10, 500), 2)}
            for i in range(1, 501)
        ]
        self.device_types = [
            "desktop", "mobile", "tablet"
        ]
        self.geo_locations = [
            {"country": "US", "city": random.choice(["New York", "San Francisco", "Chicago", "Austin"])},
            {"country": "UK", "city": random.choice(["London", "Manchester", "Liverpool"])},
            {"country": "DE", "city": random.choice(["Berlin", "Munich", "Frankfurt"])},
            {"country": "IN", "city": random.choice(["Mumbai", "Delhi", "Bangalore"])},
            {"country": "EG", "city": random.choice(["Cairo", "Alexandria", "Giza"])},
            {"country": "FR", "city": random.choice(["Paris", "Lyon", "Marseille"])},
            {"country": "ES", "city": random.choice(["Madrid", "Barcelona", "Valencia"])},
            {"country": "EG", "city": random.choice(["Cairo", "Alexandria", "Giza"])},
            {"country": "SA", "city": random.choice(["Riyadh", "Jeddah", "Mecca"])}
        ]
        
        self.event_weights = {
            'purchase': 0.25,
            'error': 0.10,
            'search': 0.25,
            'order_complete': 0.20,
            'order_failed': 0.20
        }
    
    def random_device_type(self):
        return random.choice(self.device_types)

    def random_geo_location(self):
        return random.choice(self.geo_locations)

    def random_session_duration(self, event_type):
        if event_type == "search":
            return random.randint(30, 600)  # 0.5 to 10 minutes
        elif event_type in ["purchase", "order_complete"]:
            return random.randint(300, 1800)  # 5 to 30 minutes
        elif event_type == "order_failed":
            return random.randint(60, 900)  # 1 to 15 minutes
        else:
            return random.randint(10, 3600)

    def generate_log(self):
        """Generate a single log entry with realistic e-commerce data"""
        user = random.choice(self.users)
        product = random.choice(self.products)
        event_type = random.choices(
            list(self.event_weights.keys()),
            weights=list(self.event_weights.values()),
            k=1
        )[0]

        geo = self.random_geo_location()

        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": "INFO" if event_type not in ["error", "order_failed"] else "ERROR",
            "service": "ecommerce-platform",
            "event_type": event_type,
            "user_id": user["user_id"],
            "session_id": f"sess_{random.randint(10000, 99999)}",
            "product_id": product["product_id"],
            "session_duration": self.random_session_duration(event_type),
            "device_type": self.random_device_type(),
            "geo_location": geo,
            "details": {}
        }

        # Add event-specific details
        if event_type == "purchase":
            log_entry["details"] = {
                "amount": product["price"],
                "payment_method": random.choice(["credit_card", "paypal", "bank_transfer"]),
                "items": [{
                    "product_id": product["product_id"],
                    "quantity": random.randint(1, 3)
                }],
                "shipping_address": f"{random.randint(100,999)} Main St, {geo['city']}, {geo['country']}"
            }
        elif event_type == "search":
            log_entry["details"] = {
                "query": random.choice([
                    "laptop", "shoes", "t-shirt", "book", "headphones", "sofa", "dress", "camera"
                ]),
                "results_count": random.randint(0, 50),
                "filters": random.choice([
                    {"category": "Electronics"},
                    {"price_range": "100-200"},
                    {"brand": "BrandX"},
                    {"category": "Books", "price_range": "10-50"},
                    {}
                ]),
                "searched_at": (datetime.utcnow() - timedelta(seconds=random.randint(0, 120))).isoformat() + "Z"
            }
        elif event_type == "order_complete":
            log_entry["details"] = {
                "order_id": f"order_{random.randint(100000, 999999)}",
                "amount": product["price"] * random.randint(1, 3),
                "items": [{
                    "product_id": product["product_id"],
                    "quantity": random.randint(1, 3)
                }],
                "shipping_method": random.choice(["standard", "express", "pickup"]),
                "delivery_estimate": (datetime.utcnow() + timedelta(days=random.randint(1,7))).isoformat() + "Z",
                "completed_at": (datetime.utcnow() - timedelta(seconds=random.randint(0, 180))).isoformat() + "Z"
            }
        elif event_type == "order_failed":
            log_entry["details"] = {
                "order_id": f"order_{random.randint(100000, 999999)}",
                "attempted_amount": product["price"] * random.randint(1, 3),
                "failed_at": (datetime.utcnow() - timedelta(seconds=random.randint(0, 180))).isoformat() + "Z"
            }
        elif event_type == "error":
            log_entry.update({
                "error_code": f"ERR-{random.randint(1000, 9999)}",
                "message": random.choice([
                    "Payment processing failed",
                    "Inventory check timeout",
                    "User authentication error",
                    "Product not found",
                    "Cart update failed"
                ]),
                "error_at": (datetime.utcnow() - timedelta(seconds=random.randint(0, 60))).isoformat() + "Z"
            })

        return log_entry

    def generate_logs(self, count=10, interval=0.5):
        """Generate multiple logs with time intervals"""
        logs = []
        for _ in range(count):
            log = self.generate_log()
            logs.append(log)
            time.sleep(interval)
        return logs

if __name__ == "__main__":
    generator = LogGenerator()
    
    # Generate 10 sample logs with 0.5s interval
    print("=== Generating Sample E-Commerce Logs ===")
    generator.generate_logs(count=10, interval=0.5)