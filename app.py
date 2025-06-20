from flask import Flask, render_template, jsonify
import requests
from datetime import datetime
import json
import os

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

def load_endpoints(data_folder):
    ENDPOINTS = []
    for filename in os.listdir(data_folder):
        if filename.endswith(".json"):
            file_path = os.path.join(data_folder, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    if isinstance(data, list):
                        ENDPOINTS.extend(data)
                    else:
                        ENDPOINTS.append(data)
                except json.JSONDecodeError as e:
                    print(f"Error decoding {filename}: {e}")
    return ENDPOINTS

@app.route('/list')
def get_file_name_list():
    json_folder ="data"
    file_list=[]
    for filename in os.listdir(json_folder):
        if filename.endswith(".json"):
            file_list.append(filename.replace(".json",""))
    return file_list



def build_base_url(hostname, port):
    return f"http://{hostname}:{port}" if port else f"http://{hostname}"

def collect_actuator_results(base_url):
    results = {}
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
    info_details = None
    if results['info']['status'] == 'success' and results['info']['data']:
        info_data = results['info']['data']
        java_version = info_data.get('java', {}).get('version')
        git_info = info_data.get('git', {})
        info_details = {
            'java_version': java_version,
            'git': git_info
        }
    return results, info_details

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    app_results = []
    last_checked = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data_folder = "./data"
    ENDPOINTS = load_endpoints(data_folder)
    for app_info in ENDPOINTS:
        app_name = app_info['name']
        hostname = app_info['hostname']
        port = app_info['port']
        base_url = build_base_url(hostname, port)
        results, info_details = collect_actuator_results(base_url)
        app_results.append({
            'name': app_name,
            'results': results,
            'last_checked': last_checked,
            'info_details': info_details
        })
    return jsonify({'app_results': app_results})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
