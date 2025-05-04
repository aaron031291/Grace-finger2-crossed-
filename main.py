import sys
sys.path.append("./grace_core_systems")

from central_intelligence import core_launcher
from flask import Flask

# Run Grace system logic
if __name__ == "__main__":
    core_launcher.run()

# Initialize basic web app status check
app = Flask(__name__)

@app.route("/")
def index():
    return "Grace is online and responsive."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)