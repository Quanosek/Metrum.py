from flask import Flask
from threading import Thread

app = Flask('')


@app.route('/')
def home():
  return 'Strona internetowa bota Metrum#3404!'


def run():
  app.run(host='0.0.0.0', port=8080)


def Website():
  print(' * Server is ready.')
  t = Thread(target=run)
  t.start()
