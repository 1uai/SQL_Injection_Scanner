from flask import Flask, render_template, request, jsonify
import time
import json
import Payloads_Of_SQL
import requests
from Forms_Extraction import extract_forms_selenium
from copy import deepcopy

app = Flask(__name__)

# Global variables to hold data between requests
Forms_data = {}
Input_Form = {}
Input_parameters = []

# =========================================================================================================================
# ==========================> Function: inject_payloads <==================================================================
# =========================================================================================================================
def inject_payloads(params, payloads, Payload_type):
    Injected_Forms = []
    for key in params:
        for in_input in Input_Form['input']:
            if in_input['name'] == key:  # Find the correct input field by 'name'
                for payload in payloads[Payload_type]:
                    modifies_forms = deepcopy(Input_Form)  # Deep copy the entire form
                    modifies_forms['input'] = []  # Start with an empty list for inputs

                    for field in Input_Form['input']:  # Loop through all input fields
                        modified_field = field.copy()  # Copy each field
                        if field['name'] == key:  # If it's the target field, inject the payload
                            modified_field['value'] = payload
                        modifies_forms['input'].append(modified_field)  # Keep all fields in the form

                    Injected_Forms.append(modifies_forms)  # Add the modified form with injected payload
    return Injected_Forms


# =========================================================================================================================
# ==========================> Function: send_request <====================================================================
# =========================================================================================================================
def send_request(action_url, method, data):
    try:
        if method.lower() == 'post':
            response = requests.post(action_url, data=data, timeout=10)
        else:
            response = requests.get(action_url, params=data, timeout=10)
        return response
    except requests.RequestException as e:
        print(f"Error occurred during request: {e}")
        return None


# =========================================================================================================================
# ==========================> Function: response_analyzer <===============================================================
# =========================================================================================================================
def response_analyzer(response, Payload_type, start_time=None):
    error_indicators = [  # For In-band and Error-based SQLi
        "SQL syntax", "MySQL", "ORA", "PostgreSQL", "database error",
        "SQL Server", "T-SQL", "DB2", "SQLite", "unterminated string",
        "SQLSTATE", "Warning: mysql_fetch", "Unclosed quotation mark",
        "conversion failed", "invalid input syntax"
    ]
    union_indicators = [  # For Union-based indicators
        "SELECT", 'UNION', "Column", 'from information_schema', 'table_schema',
        "database()", "user()", "version()"
    ]
    success_indicators = [
        "Welcome", "Dashboard", "Logout", "My Account", "Profile"
    ]

    if Payload_type in ["In-band", "Error-based"]:  # Detect In-band and Error-based
        for error in error_indicators:
            if error in response.text:
                print(f"SQL injection detected with payload type: {Payload_type} on error_indicator: {error}")
                return True
    if Payload_type == "Union-based":  # Detect Union-Based
        for indicators in union_indicators:
            if indicators in response.text:
                print(f"Union-Based SQL Injection detected on union_indicator: {indicators}")
                return True
    if Payload_type == "Auth-Bypass-Payloads":  # Detect Authentication Bypass
        for indicators in success_indicators:
            if indicators in response.text:
                print(f"Authentication Bypass detected on success_indicator: {indicators}")
                return True
    if Payload_type == "Time-based-blind":  # Detect Time-based Blind SQLi
        if start_time:
            response_time = time.time() - start_time
            if response_time > 6:
                print(f"Time-based SQLi detected with delay of {response_time:.2f} seconds")
                return True
    return False

@app.route('/', methods=['GET', 'POST'])
def index():
    global Forms_data, Input_Form, Input_parameters

    if request.method == 'POST':
        step = request.form.get('step') or request.json.get('step')
        
        if step == 'url':
            url = request.form.get('url')
            if not url:
                return jsonify({"error": "Please provide a valid URL"}), 400

            # Extract forms
            Forms_data = extract_forms_selenium(url, browser='firefox')
            print(f"Extracted forms: {Forms_data}")  # Debugging print statement
            extracted_forms = [{'form_id': f"Form#{i+1}", 'form_data': json.loads(form)} for i, form in enumerate(Forms_data)]
            return jsonify({"forms": extracted_forms})
        
        elif step == 'select_form':
            form_id = request.form.get('form_choice')
            print(f"Selected form_id: {form_id}")  # Debugging print statement
            print(f"Available forms: {Forms_data}")  # Debugging print statement
            # maybe issue
            print("*"*100)
            
            form_index = int(form_id.split('#')[1]) - 1  # Extract index from form_id (e.g., Form#2 -> 1)
            if form_index < len(Forms_data):
                Input_Form = json.loads(Forms_data[form_index])
                input_names = [input_field['name'] for input_field in Input_Form['input'] if input_field['name']]
                print(input_names)
                return jsonify({"input_names": input_names})
            else:
                return jsonify({"error": "Please select a valid form."}), 400
        elif step == 'select_parameters':
            print("Inside select_parameters")
            data = request.json  # Use request.json to get JSON data
            selected_params = data.get('params', [])
            
            if selected_params:
                Input_parameters = selected_params
                return jsonify({"message": "Parameters selected successfully."})
            else:
                return jsonify({"error": "Please select at least one parameter."}), 400

        
        elif step == 'perform_attack':
            Payload_type = request.form.get('attack_type')
            if not Payload_type:
                return jsonify({"error": "Please select a payload type"}), 400

            action_url = request.form.get('url') + Input_Form['action']
            method = Input_Form.get('method')
            payload_names = Payloads_Of_SQL.payloads

            # Inject payloads and perform attack
            attack_results = []
            for inject_params in inject_payloads(Input_parameters, payload_names, Payload_type):
                start_time = time.time()
                response = send_request(action_url, method, inject_params)
                if response_analyzer(response, Payload_type, start_time):
                    result = f"SQL Injection Vulnerability found with payload: {inject_params}"
                else:
                    result = "No Vulnerability detected."
                attack_results.append(result)
            
            return jsonify({"result": attack_results})

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
