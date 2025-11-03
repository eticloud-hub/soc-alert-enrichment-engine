import csv
import json
from pathlib import Path
from .database import insert_alert

def ingest_from_csv(file_path):
    """
    Ingest alerts from CSV file
    Expected columns: timestamp, source_ip, destination_ip, alert_type, message
    """
    alerts_ingested = 0

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                insert_alert(
                    timestamp=row.get('timestamp', ''),
                    source_ip=row.get('source_ip', ''),
                    destination_ip=row.get('destination_ip', ''),
                    alert_type=row.get('alert_type', ''),
                    message=row.get('message', '')
                )
                alerts_ingested += 1

        print(f"✓ Ingested {alerts_ingested} alerts from CSV")
        return alerts_ingested

    except FileNotFoundError:
        print(f"✗ File not found: {file_path}")
        return 0
    except Exception as e:
        print(f"✗ Error during ingestion: {str(e)}")
        return 0

def ingest_from_json(file_path):
    """
    Ingest alerts from JSON file
    Expected format: list of alert objects
    """
    alerts_ingested = 0

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            alerts_data = json.load(f)

            if not isinstance(alerts_data, list):
                print("✗ JSON must contain a list of alerts")
                return 0

            for alert in alerts_data:
                insert_alert(
                    timestamp=alert.get('timestamp', ''),
                    source_ip=alert.get('source_ip', ''),
                    destination_ip=alert.get('destination_ip', ''),
                    alert_type=alert.get('alert_type', ''),
                    message=alert.get('message', '')
                )
                alerts_ingested += 1

        print(f"✓ Ingested {alerts_ingested} alerts from JSON")
        return alerts_ingested

    except FileNotFoundError:
        print(f"✗ File not found: {file_path}")
        return 0
    except json.JSONDecodeError:
        print("✗ Invalid JSON format")
        return 0
    except Exception as e:
        print(f"✗ Error during ingestion: {str(e)}")
        return 0