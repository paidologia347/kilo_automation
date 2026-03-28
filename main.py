from run_pipeline import run_pipeline

import time

while True:
    try:
        print("Running pipeline...")
        run_pipeline()
    except Exception as e:
        print("Error:", e)

    time.sleep(86400)
