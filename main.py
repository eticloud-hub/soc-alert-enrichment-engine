"""Main entry point for SOC Alert Enrichment Engine"""
import sys
from pathlib import Path
import csv
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from soc_alert_engine.core.database import init_database, get_connection, get_all_alerts
from soc_alert_engine.core.ingestion import ingest_from_csv, ingest_from_json
from soc_alert_engine.core.scoring import score_alert

def export_to_csv(filename="soc_alert_engine/data/enriched_alerts.csv"):
    """Export enriched alerts to CSV"""
    alerts = get_all_alerts()
    
    if not alerts:
        print("✗ No alerts to export")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'timestamp', 'source_ip', 'destination_ip', 'alert_type', 'risk_score', 'priority', 'message']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for alert in alerts:
            writer.writerow({
                'id': alert['id'],
                'timestamp': alert['timestamp'],
                'source_ip': alert['source_ip'],
                'destination_ip': alert['destination_ip'],
                'alert_type': alert['alert_type'],
                'risk_score': alert['risk_score'],
                'priority': alert['priority'],
                'message': alert['message']
            })
    
    print(f"✓ Exported {len(alerts)} alerts to {filename}")

def export_to_json(filename="soc_alert_engine/data/enriched_alerts.json"):
    """Export enriched alerts to JSON"""
    alerts = get_all_alerts()
    
    if not alerts:
        print("✗ No alerts to export")
        return
    
    alerts_data = []
    for alert in alerts:
        alert_dict = {
            'id': alert['id'],
            'timestamp': alert['timestamp'],
            'source_ip': alert['source_ip'],
            'destination_ip': alert['destination_ip'],
            'alert_type': alert['alert_type'],
            'risk_score': alert['risk_score'],
            'priority': alert['priority'],
            'message': alert['message'],
            'enrichment_data': json.loads(alert['enrichment_data']) if alert['enrichment_data'] else {}
        }
        alerts_data.append(alert_dict)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(alerts_data, f, indent=2)
    
    print(f"✓ Exported {len(alerts)} alerts to {filename}")

def main():
    """Main execution flow"""
    print("\n" + "="*60)
    print("SOC ALERT ENRICHMENT & PRIORITIZATION ENGINE")
    print("="*60 + "\n")
    
    # 1. Initialize database
    print("[1/4] Initializing database...")
    init_database()
    
    # 2. Ingest alerts from CSV
    print("\n[2/4] Ingesting alerts from CSV...")
    ingest_from_csv("soc_alert_engine/data/alerts_sample.csv")
    
    # 3. Score all alerts
    print("\n[3/4] Scoring and enriching alerts...")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, source_ip, destination_ip, alert_type, message FROM alerts")
    alerts = cursor.fetchall()
    conn.close()
    
    scored_count = 0
    for alert in alerts:
        score_alert(alert[0], alert[1], alert[2], alert[3], alert[4])
        scored_count += 1
    
    print(f"✓ Scored {scored_count} alerts")
    
    # 4. Export results
    print("\n[4/4] Exporting enriched alerts...")
    export_to_csv()
    export_to_json()
    
    # Display summary
    print("\n" + "="*60)
    print("ALERT SUMMARY")
    print("="*60)
    
    alerts = get_all_alerts()
    high = len([a for a in alerts if a['priority'] == 'High'])
    medium = len([a for a in alerts if a['priority'] == 'Medium'])
    low = len([a for a in alerts if a['priority'] == 'Low'])
    
    print(f"Total Alerts: {len(alerts)}")
    print(f"  - High Priority:   {high}")
    print(f"  - Medium Priority: {medium}")
    print(f"  - Low Priority:    {low}")
    
    avg_score = sum([a['risk_score'] or 0 for a in alerts]) / len(alerts) if alerts else 0
    print(f"\nAverage Risk Score: {avg_score:.2f}/100")
    
    print("\n" + "="*60)
    print("✓ Pipeline complete!")
    print("✓ To view dashboard: python -m flask --app soc_alert_engine.web.app run")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
