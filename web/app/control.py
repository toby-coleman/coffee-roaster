import pandas as pd
import redis
import json


r = redis.Redis(host='redis', port=6379, db=0)


def data(topic, max_points=900, extend=True):
    payload = r.lrange(topic, 0, max_points - 1)
    if not payload:
        # No data
        return pd.DataFrame(columns=['timestamp', 'value']).set_index('timestamp')
    # Convert bytes to dicts
    df = pd.DataFrame(
        [json.loads(r) for r in payload]
    )
    df = df.assign(
        timestamp=pd.to_datetime(df.timestamp, unit='ms')
    ).set_index('timestamp').sort_index()
    # Add current timestamp as latest
    if extend:
        df = df.append(pd.DataFrame({'value': df.iloc[-1, 0]}, index=[pd.Timestamp.now()]))
    return df


def publish(topic, value):
    r.publish(topic, value)


def log(topic, value):
    r.lpush(topic, json.dump({'value': value})


def latest(topic):
    if isinstance(topic, list):
        return {t: latest(t) for t in topic}
    payload = r.lrange(topic, 0, 0)
    if not payload:
        return None
    else:
        return json.loads(payload[0]).get('value')
