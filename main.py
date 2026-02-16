import pandas as pd
from pytrends.request import TrendReq
from datetime import date
import os

# --- CONFIGURATION ---
KEYWORDS = ["Vanilla Perfume", "Oud", "Santal 33", "Cherry Perfume"] 
GEO = "US"
TIMEFRAME = "now 1-d" # Fetch last 24 hours to get fresh data points

def update_tracker():
    print("Fetching Google Trends data...")
    pytrends = TrendReq(hl='en-US', tz=360)
    
    new_data_rows = []
    
    for kw in KEYWORDS:
        try:
            pytrends.build_payload([kw], cat=0, timeframe=TIMEFRAME, geo=GEO, gprop='')
            data = pytrends.interest_over_time()
            
            if not data.empty:
                # We take the mean of the last day to get a single "daily score"
                daily_score = round(data[kw].mean(), 2)
                today_str = date.today().strftime('%Y-%m-%d')
                
                new_data_rows.append({
                    "date": today_str,
                    "keyword": kw,
                    "interest": daily_score
                })
                print(f"Got data for {kw}: {daily_score}")
        except Exception as e:
            print(f"Error for {kw}: {e}")

    if not new_data_rows:
        print("No data collected.")
        return

    # Create a DataFrame for the new data
    new_df = pd.DataFrame(new_data_rows)

    # Load existing CSV if it exists, otherwise create new
    csv_file = "trends.csv"
    if os.path.exists(csv_file):
        existing_df = pd.read_csv(csv_file)
        # Combine old and new data
        final_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        final_df = new_df

    # Remove duplicates just in case (same keyword on same day)
    final_df = final_df.drop_duplicates(subset=['date', 'keyword'], keep='last')
    
    # Save back to CSV
    final_df.to_csv(csv_file, index=False)
    print("trends.csv updated successfully.")

if __name__ == "__main__":
    update_tracker()
