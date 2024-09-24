import pandas as pd
import numpy as np
from tabulate import tabulate

def load_and_process_data(file_path):
    # Load the data
    df = pd.read_csv(file_path)
    
    # Calculate cancellation rates
    df['buyer_cancellation_rate'] = df['Lots cancelled by buyer (count)'] / (df['Lots Paid by buyer (count)'] + df['Lots cancelled by buyer (count)'])
    df['seller_cancellation_rate'] = df['Lots cancelled by seller (count)'] / (df['Lots sold by seller (count)'] + df['Lots cancelled by seller (count)'])
    
    # Identify linked accounts
    linked_accounts = df.groupby('Cookie Session ID').filter(lambda x: len(x) > 1)
    
    # Function to categorize risk
    def categorize_risk(row):
        if row.name in linked_accounts.index:
            return 'High Risk'
        elif row['buyer_cancellation_rate'] > 0.5 or row['seller_cancellation_rate'] > 0.5:
            return 'High Risk'
        elif row['buyer_cancellation_rate'] > 0.25 or row['seller_cancellation_rate'] > 0.25:
            return 'Medium Risk'
        else:
            return 'Low Risk'
    
    # Categorize users based on risk
    df['risk_category'] = df.apply(categorize_risk, axis=1)
    
    return df, linked_accounts

def analyze_data(df, linked_accounts):
    analysis = {}
    
    # Risk Segmentation
    risk_counts = df['risk_category'].value_counts()
    analysis['risk_segmentation'] = risk_counts.to_dict()
    
    # Linked Accounts
    analysis['linked_accounts'] = linked_accounts['user_id'].nunique()
    
    # Cancellation Rates
    analysis['avg_buyer_cancellation_rate'] = df['buyer_cancellation_rate'].mean()
    analysis['avg_seller_cancellation_rate'] = df['seller_cancellation_rate'].mean()
    
    # User Activity Patterns
    analysis['both_activities'] = len(df[(df['Lots Paid by buyer (count)'] > 0) & (df['Lots sold by seller (count)'] > 0)])
    analysis['only_buyers'] = len(df[(df['Lots Paid by buyer (count)'] > 0) & (df['Lots sold by seller (count)'] == 0)])
    analysis['only_sellers'] = len(df[(df['Lots Paid by buyer (count)'] == 0) & (df['Lots sold by seller (count)'] > 0)])
    
    # High Risk Users
    high_risk_users = df[df['risk_category'] == 'High Risk'].sort_values('buyer_cancellation_rate', ascending=False)
    analysis['top_10_high_risk'] = high_risk_users[['user_id', 'buyer_cancellation_rate', 'seller_cancellation_rate', 'Lots cancelled by buyer (count)', 'Lots Paid by buyer (count)', 'Lots cancelled by seller (count)', 'Lots sold by seller (count)']].head(10)
    
    return analysis

def generate_report(analysis):
    report = []
    report.append("# Catawiki Trust and Safety Analysis: Final Report\n")

    report.append("## Executive Summary\n")
    report.append("This report presents the findings of a comprehensive analysis of user behavior on the Catawiki platform, focusing on identifying potential violations and risk factors. The analysis covered 1000 users and their activities as both buyers and sellers.\n")

    report.append("## Methodology\n")
    report.append("The analysis was conducted using Python, leveraging pandas for data manipulation and analysis. Key steps included data preparation, calculation of cancellation rates, identification of linked accounts, risk categorization, and analysis of buying and selling patterns.\n")

    report.append("## Detailed Findings\n")

    # Risk Segmentation Results
    report.append("### Risk Segmentation Results\n")
    for category, count in analysis['risk_segmentation'].items():
        report.append(f"- {category}: {count} users ({count/1000*100:.1f}%)\n")

    # Linked Accounts
    report.append(f"\n### Linked Accounts\n")
    report.append(f"{analysis['linked_accounts']} users were identified as having linked accounts based on shared Cookie Session IDs.\n")

    # Cancellation Rates
    report.append("\n### Cancellation Rates\n")
    report.append(f"- Average Buyer Cancellation Rate: {analysis['avg_buyer_cancellation_rate']:.2%}\n")
    report.append(f"- Average Seller Cancellation Rate: {analysis['avg_seller_cancellation_rate']:.2%}\n")

    # User Activity Patterns
    report.append("\n### User Activity Patterns\n")
    report.append(f"- Users with both buying and selling activity: {analysis['both_activities']}\n")
    report.append(f"- Users with only buying activity: {analysis['only_buyers']}\n")
    report.append(f"- Users with only selling activity: {analysis['only_sellers']}\n")

    report.append("\n## Identified Violations and Risk Rankings\n")
    report.append("1. High Cancellation Rates (>50%) - High Risk\n")
    report.append("2. Linked Accounts - High Risk\n")
    report.append("3. Moderate Cancellation Rates (25-50%) - Medium Risk\n")
    report.append("4. Imbalanced Buying/Selling Activity - Low to Medium Risk\n")

    report.append("\n## Recommendations\n")
    report.append("1. Implement real-time monitoring of cancellation rates\n")
    report.append("2. Enhance methods to detect linked accounts\n")
    report.append("3. Develop a tiered system of interventions based on risk level\n")
    report.append("4. Create targeted educational programs for medium and high-risk users\n")
    report.append("5. Regularly reassess user risk levels\n")

    report.append("\n## Detailed Analysis of High Risk Users\n")
    report.append(tabulate(analysis['top_10_high_risk'], headers='keys', tablefmt='pipe', showindex=False))

    return "\n".join(report)

# Main execution
file_path = 'TSO_Analyst_-_Case_Study__2024_(3).csv'
df, linked_accounts = load_and_process_data(file_path)
analysis_results = analyze_data(df, linked_accounts)
report = generate_report(analysis_results)

with open('catawiki_analysis_report.md', 'w') as f:
    f.write(report)