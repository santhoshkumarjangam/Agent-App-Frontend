from flask import Flask, render_template, redirect, url_for, request
import json
import requests

app = Flask(__name__)

@app.route("/")
def home():
    response = requests.get(
            url="http://127.0.0.1:8080/get-agents"
        )
    data = response.json()
    single_agents = data.get("single_agents", [])
    multi_agents = data.get("multi_agents", [])

    return render_template('index.html', single_agents=single_agents[::-1], multi_agents=multi_agents[::-1])

@app.route("/create-single-agent", methods=["GET", "POST"])
def create_single_agent():
    if request.method == "POST":
        response = requests.post(
            url="http://127.0.0.1:8080/create-single-agent",
            json={"name": request.form.get("name"),
                  "model": request.form.get("model"),
                  "description": request.form.get("description"),
                  "instruction": request.form.get("instruction"),
                  "tools": request.form.getlist("tools")
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
            "tools": request.form.getlist("main_tools")
        }

        sub_names = request.form.getlist("sub_name[]")
        sub_models = request.form.getlist("sub_model[]")
        sub_descriptions = request.form.getlist("sub_description[]")
        sub_instructions = request.form.getlist("sub_instructions[]")

        sub_agents = []
        for i in range(len(sub_names)):
            tools = request.form.getlist(f"sub_tools[{i}][]")
            sub_agents.append({
                "name": sub_names[i],
                "model": sub_models[i],
                "description": sub_descriptions[i],
                "instruction": sub_instructions[i],
                "tools": tools
            })

        payload = {
            "name": main_agent_data["name"],
            "model": main_agent_data["model"],
            "description": main_agent_data["description"],
            "instruction": main_agent_data["instruction"],
            "tools": main_agent_data["tools"],
            "subagents": sub_agents
        }

        print(payload)

        response = requests.post(
            url="http://127.0.0.1:8080/create-multi-agent",
            json=payload
        )
        return redirect(url_for('home'))

    return render_template("createMultiAgent.html")

@app.route('/delete/<string:agent_type>/<int:agent_id>')
def delete_agent(agent_type, agent_id):
    response = requests.post(url=f"http://127.0.0.1:8080/delete/{agent_type}/{agent_id}")

    return redirect(url_for("home"))

@app.route('/chat/<string:agent_type>/<int:agent_id>', methods=["GET", "POST"])
def chat(agent_id, agent_type):
    if request.method == "POST":
        prompt = request.form.get("prompt")
        
        response = requests.post(
            url = f"http://127.0.0.1:8080/interact/{agent_type}/{agent_id}",
            json={"user_id":"new-user","message":str(prompt)}
        )

        return render_template('chatInterface.html', response=response.json().get('response'), prompt=prompt, agent_id=agent_id, agent_type=agent_type)

    return render_template('chatInterface.html', response="", prompt=None, agent_id=agent_id, agent_type=agent_type)

if __name__ == "__main__":
    app.run(debug=True)