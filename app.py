from flask import Flask, render_template, redirect, url_for, request

import requests

app = Flask(__name__)

@app.route("/")
def home():
    response = requests.get(
            url="http://127.0.0.1:8000/get-agents"
        )
    data = response.json()
    single_agents = data.get("single_agents", [])
    multi_agents = data.get("multi_agents", [])

    return render_template('index.html', single_agents=single_agents[::-1], multi_agents=multi_agents[::-1])

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
    if request.method == "POST":
        main_agent_data = {
            "name": request.form.get("name"),
            "model": request.form.get("model"),
            "description": request.form.get("description"),
            "instruction": request.form.get("instruction"),
        }

        sub_names = request.form.getlist("sub_name[]")
        sub_models = request.form.getlist("sub_model[]")
        sub_descriptions = request.form.getlist("sub_description[]")
        sub_instructions = request.form.getlist("sub_instructions[]")

        sub_agents = []
        for i in range(len(sub_names)):
            sub_agents.append({
                "name": sub_names[i],
                "model": sub_models[i],
                "description": sub_descriptions[i],
                "instruction": sub_instructions[i],
            })

        payload = {
            "name": main_agent_data["name"],
            "model": main_agent_data["model"],
            "description": main_agent_data["description"],
            "instruction": main_agent_data["instruction"],
            "subagents": sub_agents
        }

        response = requests.post(
            url="http://127.0.0.1:8000/create-multi-agent",
            json=payload
        )
        return redirect(url_for('home'))

    return render_template("createMultiAgent.html")

@app.route('/chat/<string:agent_type>/<int:agent_id>', methods=["GET", "POST"])
def chat(agent_id, agent_type):
    if request.method == "POST":
        prompt = request.form.get("prompt")
        
        response = requests.post(
            url = f"http://127.0.0.1:8000/interact/{agent_type}/{agent_id}",
            json={"user_id":"new-user","message":str(prompt)}
        )

        return render_template('chatInterface.html', response=response.json().get('response'), agent_id=agent_id, agent_type=agent_type)

    return render_template('chatInterface.html', response="", agent_id=agent_id, agent_type=agent_type)

if __name__ == "__main__":
    app.run(debug=True)