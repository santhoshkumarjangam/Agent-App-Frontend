from flask import Flask, render_template, redirect, url_for, request

import requests

app = Flask(__name__)

@app.route("/")
def home():
    response=""
    response = requests.get(
            url="http://127.0.0.1:8000/get-agents"
        )
    agents = response.json().get("agents", [])

    return render_template('index.html', agents=agents[::-1])

@app.route("/create-single-agent", methods=["GET", "POST"])
def create_single_agent():
    if request.method == "POST":
        response = requests.post(
            url="http://127.0.0.1:8000/create-single-agent",
            json={"name": request.form.get("name"),
                  "model": request.form.get("model"),
                  "description": request.form.get("description"),
                  "instruction": request.form.get("instruction")
                }
        )
        return redirect(url_for('home'))

    return render_template('createSingleAgent.html')

@app.route("/create-multi-agent", methods=["GET", "POST"])
def create_multi_agent():
    return render_template('createMultiAgent.html')

@app.route('/chat/<int:agent_id>', methods=["GET", "POST"])
def chat(agent_id):
    if request.method == "POST":
        prompt = request.form.get("prompt")
        
        response = requests.post(
            url = f"http://127.0.0.1:8000/interact/{agent_id}",
            json={"user_id":"charan","message":str(prompt)}
        )

        return render_template('chatInterface.html', response=response.json(), agent_id=agent_id)

    return render_template('chatInterface.html', response="", agent_id=agent_id)

if __name__ == "__main__":
    app.run(debug=True)