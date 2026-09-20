from __future__ import annotations

import threading
import time

from depdigest import dep_digest

from ..core.collector import get_used_items
from ..core.registry import Registry


@dep_digest("flask")
def serve_ui(port: int = 8080):
    """
    Start a temporary local web server to display citations.
    This is a conceptual stub for the 0.4.0 release.
    """
    from flask import Flask, render_template_string

    app = Flask(__name__)

    @app.route("/")
    def index():
        used = get_used_items()
        items = Registry.items

        # Simple HTML template
        html = """
        <html>
        <head><title>Ackredit Live Dashboard</title></head>
        <body style='font-family: sans-serif; padding: 20px;'>
            <h1>Ackredit Live Citation Dashboard</h1>
            <table border='1' cellpadding='10' style='border-collapse: collapse; width: 100%;'>
                <tr><th>Item</th><th>Type</th><th>DOI</th><th>Used By</th></tr>
                {% for id, callers in used.items() %}
                <tr>
                    <td>{{ items[id].title if id in items else id }}</td>
                    <td>{{ items[id].type if id in items else 'N/A' }}</td>
                    <td>{{ items[id].doi if id in items else '-' }}</td>
                    <td>{{ callers | join(', ') }}</td>
                </tr>
                {% endfor %}
            </table>
        </body>
        </html>
        """
        return render_template_string(html, used=used, items=items)

    print(f"Starting Ackredit UI at http://127.0.0.1:{port}")
    # We run in a thread to not block the script
    thread = threading.Thread(
        target=lambda: app.run(port=port, debug=False, use_reloader=False)
    )
    thread.daemon = True
    thread.start()
    time.sleep(1)  # Give it a second to start
