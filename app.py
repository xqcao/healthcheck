from flask import Flask, render_template, jsonify
import requests
from datetime import datetime
import json

app = Flask(__name__)

# ENDPOINTS = [
#     {
#         "name": "prod page",
#         "hostname": "localhost.v1",
#         "port": "8081"
#     },
#     {
#         "name": "user check page",
#         "hostname": "localhost.v2",
#         "port": "8082"
#     },
#     {
#         "name": "car details page",
#         "hostname": "localhost.v3",
#         "port": ""
#     },
#     {
#         "name": "dog details page",
#         "hostname": "localhost.v5",
#         "port": ""
#     }
# ]

ACTUATOR_PATHS = {
    'health': '/actuator/health',
    'info': '/actuator/info',
    'metrics': '/actuator/metrics'
}

def check_endpoint(url):
    try:
        response = requests.get(url, timeout=5)
        status = 'success' if response.status_code == 200 else 'error'
        return {
            'status': status,
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds(),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data': response.json() if status == 'success' else None
        }
    except requests.RequestException as e:
        return {
            'status': 'error',
            'status_code': None,
            'response_time': None,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': str(e),
            'data': None
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    app_results = []
    last_checked = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ENDPOINTS=[]
    with open("data1.json","+r") as f1:
        ENDPOINTS = json.load(f1)
    for app_info in ENDPOINTS:
        app_name = app_info['name']
        hostname = app_info['hostname']
        port = app_info['port']
        if port:
            base_url = f"http://{hostname}:{port}"
        else:
            base_url = f"http://{hostname}"
        results = {}
        info_details = None
        for key, path in ACTUATOR_PATHS.items():
            url = base_url + path
            print("check url: "+url)
            result = check_endpoint(url)
            results[key] = {
                'url': url,
                'status': result['status'],
                'status_code': result['status_code'],
                'response_time': result['response_time'],
                'data': result['data']
            }
        # Parse info details if info is successful
        if results['info']['status'] == 'success' and results['info']['data']:
            info_data = results['info']['data']
            java_version = info_data.get('java', {}).get('version')
            git_info = info_data.get('git', {})
            info_details = {
                'java_version': java_version,
                'git': git_info
            }
        app_results.append({
            'name': app_name,
            'results': results,
            'last_checked': last_checked,
            'info_details': info_details
        })
    return jsonify({'app_results': app_results})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
