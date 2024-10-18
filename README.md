#SQL Injection Scanner
<pre>
This project is a SQL Injection Scanner built with Flask to help detect vulnerabilities in web forms by simulating different types of SQL injection attacks. It extracts forms from a target website, allows users to select form fields, and tests them using various SQL injection payloads.
Features

    Extracts and displays input forms from a given URL.
    Provides options to choose specific form fields for SQL injection testing.
    Supports multiple SQL injection types including:
        In-band SQL Injection
        Union-based SQL Injection
        Error-based SQL Injection
        Time-based Blind SQL Injection
        Authentication Bypass Payloads
    Sends injected forms with payloads and analyzes the response for SQL injection vulnerabilities.

    Project Structure
/SQL_Injection_Scanner
│
├── /static
│   └── /CSS                  
│
├── /templates
│   └── /HTML                 
│
├── Flask_app.py              
├── Payloads_Of_SQL.py         
├── Forms_Extraction.py
  
  Usage

    Start the Flask server:

    python Flask_app.py
python Flask_app.py
Open your web browser and go to http://localhost:5000.
Enter the URL of the target website. The app will display the forms found on the page.
Select a form, choose input parameters to inject, and choose the type of SQL injection attack.
The app will perform the attack and display the results of the scan.
</pre>
