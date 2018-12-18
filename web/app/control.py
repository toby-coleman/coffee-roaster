import pandas as pd
import redis
import json


r = redis.Redis(host='redis', port=6379, db=0)


def data(topic, max_points=1800):
    payload = r.lrange(topic, 0, max_points)
    if not payload:
        # No data
        return pd.DataFrame(columns=['timestamp', 'value']).set_index('timestamp')
    # Convert bytes to dicts
    df = pd.DataFrame(
        [json.loads(r) for r in payload]
    )
    df = df.assign(
        timestamp=pd.to_datetime(df.timestamp, unit='ms')
    ).set_index('timestamp')
    return df.sort_index()


def publish(topic, value):
    r.publish(topic, value)
