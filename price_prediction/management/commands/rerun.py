from subprocess import call
import time

while True:
    call(["flake8","generate_arima_model.py"])
    print()
    print()
    print()
    print()
    time.sleep(60)
