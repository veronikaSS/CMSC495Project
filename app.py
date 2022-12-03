""" This program runs the web app on local host port 5000."""
from budget_tracker import routes
from flask import Flask


if __name__ == '__main__':
    routes.app.run(debug=True, port=5000)
