from grace_core_systems.central_intelligence import core_launcher

if __name__ == "__main__":
    core_launcher.run()

from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Grace is online and responsive."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)