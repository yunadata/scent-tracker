import pandas as pd
from pytrends.request import TrendReq
from datetime import date
import os
import time

# --- CONFIGURATION ---
# We track BROAD categories now, not specific scents.
# This casts a wide net to catch anything related to these words.
SEED_TERMS = ["Perfume", "Fragrance", "Cologne", "Scent"] 
GEO = "US"
TIMEFRAME = "now 7-d" # Look at the last 7 days for fast-moving trends

def discover_trends():
    print("Starting Trend Discovery...")
    pytrends = TrendReq(hl='en-US', tz=360)
    
    discovered_data = []
    
    # Google hates it if you ask too many questions too fast, so we do one by one.
    for term in SEED_TERMS:
        print(f"Scanning for trends related to: {term}")
        try:
            pytrends.build_payload([term], cat=0, timeframe=TIMEFRAME, geo=GEO)
            
            # Get related queries
            related = pytrends.related_queries()
            
            # We only want the 'rising' dictionary
            rising_df = related[term]['rising']
            
            if rising_df is not None and not rising_df.empty:
                # Add metadata so we know where this trend came from
                rising_df['seed_term'] = term
                rising_df['date'] = date.today().strftime('%Y-%m-%d')
                
                # "Breakout" means the search volume grew by >5000%
                # We replace 'Breakout' with a high number (e.g., 5000) so we can sort it in Looker
                rising_df['value'] = rising_df['value'].replace('Breakout', 5000)
                
                discovered_data.append(rising_df)
                print(f"Found {len(rising_df)} rising trends for {term}")
            
            # Sleep for 6 seconds to be nice to Google's servers
            time.sleep(6)
            
        except Exception as e:
            print(f"Error scanning {term}: {e}")

    if not discovered_data:
        print("No new trends found today.")
        return

    # Combine all found trends
    new_df = pd.concat(discovered_data)
    
    # Rename columns for clarity
    new_df.rename(columns={'query': 'trend_name', 'value': 'growth_score'}, inplace=True)

    # --- SAVING LOGIC (APPEND MODE) ---
    csv_file = "discovered_trends.csv"
    
    if os.path.exists(csv_file):
        existing_df = pd.read_csv(csv_file)
        final_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        final_df = new_df

    # Remove duplicates: If we catch "Kitten Fur" twice on the same day via different seed terms, keep the higher score
    final_df = final_df.sort_values('growth_score', ascending=False)
    final_df = final_df.drop_duplicates(subset=['date', 'trend_name'], keep='first')
    
    # Save
    final_df.to_csv(csv_file, index=False)
    print("Success! discovered_trends.csv updated.")

if __name__ == "__main__":
    discover_trends()
