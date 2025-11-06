from flask import Flask, render_template, request, make_response
import markdown
from collections import deque
import nh3

app = Flask(__name__)

notes = []
recent_users = deque(maxlen=3)
allowed_tags = {"p", "strong", "em", "a", "code", "pre", "ul", "li"}
allowed_attrs = {"a": {"href", "title"}}


@app.route("/")
def username():
    return render_template("main.html")

@app.route("/hello", methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        username = request.form.get("username", "unknown")
        if not username in recent_users:
            recent_users.append(username)
        resp = make_response(render_template("hello.html", username=username, notes=notes, recent_users=list(recent_users)))
        resp.set_cookie("username", username)
        return resp
    if request.method == 'GET':
        username = request.cookies.get("username", "unknown")
        return render_template("hello.html", username=username, notes=notes, recent_users=list(recent_users))

@app.route("/render", methods=['POST'])
def render():
    md = request.form.get("markdown", "")
    rendered = markdown.markdown(md, extensions=["extra", "codehilite"])
    safe_rendered = nh3.clean(
        rendered,
        tags=allowed_tags,
        attributes=allowed_attrs
    )
    notes.append(safe_rendered)
    return render_template("markdown.html", rendered=safe_rendered)

@app.route("/render/<rendered_id>")
def render_old(rendered_id):
    if int(rendered_id) > len(notes):
        return "Wrong note id", 404

    rendered = notes[int(rendered_id) - 1]
    return render_template("markdown.html", rendered=rendered)

if __name__ == "__main__":
     app.run(host="127.0.0.1", port=5000, debug=True)