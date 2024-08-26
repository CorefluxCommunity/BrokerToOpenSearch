import json
import os
import signal
import sys
import time
from datetime import datetime
import threading
import paho.mqtt.client as mqtt
from opensearchpy import OpenSearch
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Mqtt Configs
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_TOPIC = "Machine/Produce"
MQTT_FEEDBACK_TOPIC = "Machine/Produce/Feedback"
MQTT_CLIENT_ID = "MqttAggregator"
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

# OpenSearch configs
OS_HOST = os.getenv("OPENSEARCH_HOST")
OS_USERNAME = os.getenv("OPENSEARCH_USERNAME")
OS_PASSWORD = os.getenv("OPENSEARCH_PASSWORD")
INDEX_NAME = "machine-production"

# OpenSearch client setup
def setup_opensearch_client():
    es = OpenSearch(
        [f"{OS_HOST}:25060"],
        http_auth=(OS_USERNAME, OS_PASSWORD),
        use_ssl=True,
        verify_certs=True,
        ssl_show_warn=False
    )
    return es 



# Shutdown flag and Signal Handler for shutdown
terminate_flag = False

def signal_handler(signum, frame):
    global terminate_flag
    print("Shutting Down...")
    terminate_flag = True

# MQTT on_connect callback
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT Broker. ResultCode = {rc}")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"Failed to connect... {rc}")

# MQTT on_disconnect callback
def on_disconnect(client, userdata, rc):
    print("Disconnected from MQTT Broker. Reconnecting...")
    while not terminate_flag:
        try:
            client.reconnect()
            break
        except Exception as e:
            print(f"Reconnection failed: {e}")
            time.sleep(5)
    
# MQTT on_message callbacl
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        print(f"Decoded payload: {payload}")
        print(f"Message received on topic {msg.topic}: {payload}")

        success = index_to_opensearch(userdata['es'], INDEX_NAME, payload)

        feedback_payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success" if success else "error",
            "message": f"Payload {'indexed successfully' if success else 'was not indexed'}"
 
        }

        publish_feedback(client, MQTT_FEEDBACK_TOPIC, feedback_payload)

    except Exception as e:
        print(f"Failed to process payload: {e}")

# Function to index data into OS
def index_to_opensearch(es, index_name, document):
    try:
        res = es.index(index=index_name, body=document)
        if res['result'] == 'created':
            print(f"Document indexed successfully in OpenSearch")
            return True
        else:
            print(f"Failed to index document: {res}")
            return False
    except Exception as e:
        print(f"Failed to index document: {e}")
        return False
    

# Function to publish feedback to MQTT
def publish_feedback(client, topic, payload):
    result = client.publish(topic, json.dumps(payload))
    status = result.rc
    if status == 0:
        print(f"Successfully sent feedback `{payload}` to topic `{topic}`")
    else:
        print (f"Failed to send feedback to topic {topic}")

# Main Function
def main():
    global terminate_flag

    es = setup_opensearch_client()

    client = mqtt.Client(MQTT_CLIENT_ID)
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.tls_set()
    client.user_data_set({'es': es})
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message



    # Connect to broker

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        print(f"Error connecting to MQTT Broker: {e}")
        return
    
    client.loop_start()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while not terminate_flag:
        time.sleep(1)

    
    client.loop_stop()
    client.disconnect()
    print("MQTT client disconnected successfully")

if __name__ == "__main__":
    main()
