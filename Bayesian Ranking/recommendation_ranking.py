import requests
import json
import pandas as pd
import numpy as np
import pickle
import logging
import pytz
from datetime import datetime
import uvicorn
from fastapi import FastAPI

app = FastAPI()

headers = {
    'Content-Type': 'application/json'
}

@app.post('/reels-ordering')
def get_order(env = 'dev'):
    tz = pytz.timezone("Asia/Calcutta")
    logging.basicConfig(level=logging.INFO, filename='reels.log', filemode='a')
    def add_log(status, message):
        cur_time = datetime.now(tz=tz).strftime("%d-%m-%Y %H:%M:%S")
        logging.info(f" {cur_time} : {status}:{message}")
    
    try:
        configs = pickle.load(open('config.pkl', 'rb'))
        complete_view_ratio = configs['complete_view_ratio']
        view_threshold = configs['view_threshold']
        factor = configs['factor']
        initial_bias = configs['initial_bias']

        views_query = "select reelId, count(*) as views from view where watchDuration >= " + str(view_threshold) + " group by reelId limit 1000000;"
        r = json.loads(requests.request("POST", urls[env]['receive_url'], headers=headers, data=json.dumps({"sql" : views_query})).text)
        df1 = pd.DataFrame(r['resultTable']['rows'], columns = r['resultTable']['dataSchema']['columnNames'])        

        complete_views_query = "select reelId, count(*) as complete_views from view where watchDuration/videoDuration >=" + str(complete_view_ratio) + " group by reelId limit 1000000;"
        r = json.loads(requests.request("POST", urls[env]['receive_url'], headers=headers, data=json.dumps({"sql" : complete_views_query})).text)
        df2 = pd.DataFrame(r['resultTable']['rows'], columns = r['resultTable']['dataSchema']['columnNames'])

        df = pd.merge(df1, df2, how='left', on='reelId').fillna(0)
        reels = list(df.values)
        reels_var = [(x[0], np.random.beta(initial_bias+1+factor*x[2], 1+factor*(x[1]-x[2]))) for x in reels]
        output = sorted(reels_var, key=lambda x : x[1], reverse=True)
        data = {
            "initialScore": 0,
            "list": [x[0] for x in output]
        }
        response = requests.request("POST", urls[env]['send_url'], headers=headers, data=json.dumps(data))
    except Exception as e:
        return add_log("ERROR", e)
    return add_log("INFO", "Success")

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
#uvicorn recommend_logs_app:app --reload
