from flask import Flask, render_template
import requests
from datetime import datetime

app = Flask(__name__)

ENDPOINTS = [
    {
        "name":"prod page",
        "hostname":"localhost.v1",
        "port":8081
    },
    {
        "name":"user check page",
        "hostname":"localhost.v2",
        "port":8082
    }
]

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
    results = {}
    last_checked = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for key, url in ENDPOINTS.items():
        result = check_endpoint(url)
        results[key] = {
            'url': url,
            'status': result['status'],
            'status_code': result['status_code'],
            'response_time': result['response_time'],
            'data': result['data']
        }
    # Parse info details if info is successful
    info_details = None
    if results['info']['status'] == 'success' and results['info']['data']:
        info_data = results['info']['data']
        # Example: extract java version, git info, etc.
        java_version = info_data.get('java', {}).get('version')
        git_info = info_data.get('git', {})
        info_details = {
            'java_version': java_version,
            'git': git_info
        }
    return render_template('index.html', results=results, last_checked=last_checked, info_details=info_details)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
