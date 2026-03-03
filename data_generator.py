import pandas as pd
import random
from datetime import datetime, timedelta

def generate_spm_test_data(num_records=50):
    portfolios = ["Digital Transformation", "Cloud Migration", "Customer Experience", "HR Excellence"]
    states = ["Draft", "Submitted", "Screening", "Qualified", "Approved", "Completed"]
    priorities = ["1 - Critical", "2 - High", "3 - Moderate", "4 - Low"]
    
    data = []
    start_date = datetime(2024, 1, 1)

    for i in range(num_records):
        proj_id = f"PRJ{1000 + i}"
        demand_id = f"DMN{5000 + i}"
        duration = random.randint(30, 180)
        end_date = start_date + timedelta(days=duration)
        
        # Mocking ServiceNow SPM Schema
        record = {
            "Demand ID": demand_id,
            "Project ID": proj_id,
            "Short Description": f"Implementation of {random.choice(['AI Chatbot', 'ERP Sync', 'Security Layer', 'Mobile Portal'])} Phase {random.randint(1,3)}",
            "Portfolio": random.choice(portfolios),
            "State": random.choice(states),
            "Priority": random.choice(priorities),
            "Planned Cost ($)": random.randint(50000, 500000),
            "Actual Cost ($)": random.randint(40000, 450000),
            "Business Value": random.choice(["Strategic", "Operational", "Compliance"]),
            "Risk Score": random.randint(1, 10),
            "Start Date": start_date.strftime("%Y-%m-%d"),
            "End Date": end_date.strftime("%Y-%m-%d")
        }
        data.append(record)
        # Increment start date slightly for variety
        start_date += timedelta(days=random.randint(1, 5))

    df = pd.DataFrame(data)
    df.to_csv("spm_sample_data.csv", index=False)
    print("✅ Success: 'spm_sample_data.csv' has been generated!")

if __name__ == "__main__":
    generate_spm_test_data()