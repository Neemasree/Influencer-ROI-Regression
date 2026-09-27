"""
Dataset Generator for Influencer Marketing ROI Project
Generates 200 rows of realistic synthetic influencer campaign data
"""

import pandas as pd
import numpy as np

np.random.seed(42)
n = 200

# --- Influencer Tiers ---
# Nano: <10K | Micro: 10K-100K | Macro: 100K-1M | Mega: 1M+
tiers      = np.random.choice(['Nano', 'Micro', 'Macro', 'Mega'], n,
                               p=[0.25, 0.40, 0.25, 0.10])
platforms  = np.random.choice(['Instagram', 'YouTube', 'TikTok', 'Twitter'], n,
                               p=[0.40, 0.25, 0.25, 0.10])
niches     = np.random.choice(['Fashion', 'Tech', 'Food', 'Travel', 'Fitness',
                                'Beauty', 'Gaming'], n)

# --- Followers based on tier ---
followers = np.where(tiers == 'Nano',
                np.random.randint(1000, 10000, n),
            np.where(tiers == 'Micro',
                np.random.randint(10000, 100000, n),
            np.where(tiers == 'Macro',
                np.random.randint(100000, 1000000, n),
                np.random.randint(1000000, 5000000, n))))

# --- Engagement Rate: higher for Nano/Micro ---
eng_base = np.where(tiers == 'Nano',  np.random.uniform(5.0, 12.0, n),
           np.where(tiers == 'Micro', np.random.uniform(3.0,  8.0, n),
           np.where(tiers == 'Macro', np.random.uniform(1.5,  4.5, n),
                                       np.random.uniform(0.5,  2.5, n))))
engagement_rate = np.round(eng_base, 2)

# --- Likes, Comments, Shares derived from followers + engagement ---
likes    = np.round(followers * engagement_rate / 100 * np.random.uniform(0.7, 1.0, n)).astype(int)
comments = np.round(likes * np.random.uniform(0.03, 0.12, n)).astype(int)
shares   = np.round(likes * np.random.uniform(0.01, 0.08, n)).astype(int)

# --- Campaign Cost (INR) ---
cost_base = np.where(tiers == 'Nano',  np.random.randint(2000,  15000,  n),
            np.where(tiers == 'Micro', np.random.randint(15000, 80000,  n),
            np.where(tiers == 'Macro', np.random.randint(80000, 500000, n),
                                        np.random.randint(500000,2000000,n))))
campaign_cost = cost_base.astype(float)

# --- Revenue: engagement and cost drive revenue ---
# Higher engagement → better conversion → more revenue
revenue_multiplier = (
    1.5
    + (engagement_rate / 10)         # engagement bonus
    + np.random.normal(0, 0.4, n)    # random noise
)
revenue_multiplier = np.clip(revenue_multiplier, 0.3, 5.0)
revenue = np.round(campaign_cost * revenue_multiplier, 2)

# --- ROI = (Revenue - Cost) / Cost ---
roi = np.round((revenue - campaign_cost) / campaign_cost, 4)

# --- Campaign Duration ---
campaign_duration_days = np.random.randint(7, 90, n)

# --- Post Frequency ---
post_frequency = np.random.randint(1, 15, n)

# --- Assemble DataFrame ---
df = pd.DataFrame({
    'Campaign_ID'           : [f'CAMP{str(i+1).zfill(3)}' for i in range(n)],
    'Platform'              : platforms,
    'Niche'                 : niches,
    'Influencer_Tier'       : tiers,
    'Followers'             : followers,
    'Likes'                 : likes,
    'Comments'              : comments,
    'Shares'                : shares,
    'Engagement_Rate'       : engagement_rate,
    'Campaign_Cost'         : campaign_cost,
    'Revenue'               : revenue,
    'Campaign_Duration_Days': campaign_duration_days,
    'Post_Frequency'        : post_frequency,
    'ROI'                   : roi
})

# Save
df.to_csv('influencer_marketing.csv', index=False)
print(f"Dataset saved: {len(df)} rows x {len(df.columns)} columns")
print(df.head())
print("\nBasic Stats:")
print(df[['Followers','Engagement_Rate','Campaign_Cost','Revenue','ROI']].describe().round(2))
