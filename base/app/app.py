from flask import Flask
from request import Requests
from random import randint
import os

app = Flask(__name__)

@app.route("/")
def route():
    count = request.args.get("count") # How far to iterate
    identity = os.getenv("identity") # Identity of the running service
    services = os.getenv("services") # The amount of services running
    if count > services:
        return "Count cannot be greater than the amount of services"
    if count != 0: # End once the count reaches 0
        for x in range (identity, services+1): # Prevent circular calls
            if randint(0, 2) % 2 == 0: # Add some randomness to the demo
                print(request.post("http://url:5000/".format(x), params={'count': count-1}))
    return "Service {} with {} calls help".format(identity, count)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True,host='0.0.0.0',port=port)