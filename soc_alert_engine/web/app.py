"""Flask web dashboard for alert visualization"""
from flask import Flask, render_template, request, jsonify
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from soc_alert_engine.core.database import get_all_alerts, get_alerts_by_priority, init_database

app = Flask(__name__, template_folder='templates')
app.config['JSON_SORT_KEYS'] = False

@app.route('/')
def dashboard():
    """Main dashboard view"""
    alerts = get_all_alerts()
    return render_template('dashboard.html', alerts=alerts)

@app.route('/api/alerts')
def api_alerts():
    """API endpoint to fetch alerts"""
    priority = request.args.get('priority', None)
    
    if priority:
        alerts = get_alerts_by_priority(priority)
    else:
        alerts = get_all_alerts()
    
    # Convert alerts to JSON-serializable format
    alerts_data = []
    for alert in alerts:
        alert_dict = {
            'id': alert['id'],
            'timestamp': alert['timestamp'],
            'source_ip': alert['source_ip'],
            'destination_ip': alert['destination_ip'],
            'alert_type': alert['alert_type'],
            'message': alert['message'],
            'risk_score': alert['risk_score'],
            'priority': alert['priority'],
            'enrichment_data': json.loads(alert['enrichment_data']) if alert['enrichment_data'] else {}
        }
        alerts_data.append(alert_dict)
    
    return jsonify(alerts_data)

@app.route('/api/stats')
def api_stats():
    """API endpoint for dashboard statistics"""
    alerts = get_all_alerts()
    
    high_count = len([a for a in alerts if a['priority'] == 'High'])
    medium_count = len([a for a in alerts if a['priority'] == 'Medium'])
    low_count = len([a for a in alerts if a['priority'] == 'Low'])
    
    avg_score = sum([a['risk_score'] or 0 for a in alerts]) / len(alerts) if alerts else 0
    
    return jsonify({
        'total_alerts': len(alerts),
        'high_priority': high_count,
        'medium_priority': medium_count,
        'low_priority': low_count,
        'avg_risk_score': round(avg_score, 2)
    })

if __name__ == '__main__':
    init_database()
    app.run(debug=True, port=5000)
