from flask import Flask, render_template_string
import sqlite3

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Australia GP Intelligence Portal</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light p-4">
    <div class="container bg-white p-4 rounded shadow-sm">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h2 class="text-primary fw-bold">🇦🇺 Australia General Practitioner Data Portal</h2>
                <p class="text-muted mb-0">Automated Web Scraping & AI Entity Resolution Pipeline</p>
            </div>
            <span class="badge bg-success fs-6">Live Intelligence Stream</span>
        </div>
        <hr>
        <div class="table-responsive">
            <table class="table table-hover table-bordered align-middle">
                <thead class="table-dark">
                    <tr>
                        <th>Practice Name</th>
                        <th>Practitioner</th>
                        <th>Address</th>
                        <th>State</th>
                        <th>Postcode</th>
                        <th>Contact Phone</th>
                        <th>Bulk Billing</th>
                        <th>Specialties / Services</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in records %}
                    <tr>
                        <td><strong>{{ row[1] }}</strong></td>
                        <td>{{ row[2] }}</td>
                        <td>{{ row[3] }}, {{ row[4] }}</td>
                        <td><span class="badge bg-info text-dark">{{ row[5] }}</span></td>
                        <td>{{ row[6] }}</td>
                        <td><code>{{ row[7] }}</code></td>
                        <td>
                            {% if row[8] == 'Yes' %}
                                <span class="badge bg-success">Yes</span>
                            {% else %}
                                <span class="badge bg-secondary">No</span>
                            {% endif %}
                        </td>
                        <td><small>{{ row[9] }}</small></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    conn = sqlite3.connect("gp_australia_intelligence.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM general_practitioners")
    records = cursor.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, records=records)

if __name__ == '__main__':
    app.run(debug=True, port=5000)