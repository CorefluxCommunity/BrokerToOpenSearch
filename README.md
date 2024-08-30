# Coreflux to OpenSearch Integration Script

This script facilitates the integration between a Coreflux MQTT broker and an OpenSearch instance hosted on DigitalOcean. The script listens to MQTT messages from the Coreflux broker, processes the payload, and stores the data in the specified OpenSearch index. It also provides feedback on the success of data indexing.

## Prerequisites

Before using this script, ensure you have the following:

1. A Coreflux MQTT broker with valid credentials.
2. Mqtt Explorer to publish messages in the broker.
3. A DigitalOcean OpenSearch instance with connection details.
4. Python environment with the necessary libraries installed:

   ```bash
   pip install paho-mqtt opensearch-py python-dotenv

# Setup Instructions

### 1. Clone or Download the Script
First, download the script to your local machine or clone it from the repository.

### 2. Configure Environment Variables
Create a .env file in the same directory as your script and populate it with the following variables:

```bash
  MQTT_BROKER=<your-coreflux-broker-url>
  MQTT_PORT=8883  # Default MQTT port with SSL, change if using a different one
  MQTT_USERNAME=<your-coreflux-username>
  MQTT_PASSWORD=<your-coreflux-password>

  OPENSEARCH_HOST=<your-opensearch-host-url>
  OPENSEARCH_USERNAME=<your-opensearch-username>
  OPENSEARCH_PASSWORD=<your-opensearch-password>
```
### 3. Customize the Script (Optional)

You can customize the following variables within the script to suit your specific needs:

- **`MQTT_TOPIC`**: The topic your devices are publishing messages to. 
  - Default: `"Machine/Produce"`
  - Modify this if your IoT devices publish data to a different topic.

- **`MQTT_FEEDBACK_TOPIC`**: The topic where feedback messages are published.
  - Default: `"Machine/Produce/Feedback"`
  - Change this if you want feedback to be sent to a different topic.

- **`INDEX_NAME`**: The name of the index in OpenSearch where data will be stored.
  - Default: `"machine-production"`
  - Update this if you want to store the data in a different index.

### 4. Running the Script

After configuring your environment variables and making any necessary customizations, you can run the script using the following command:

```bash
python mqttToOS.py
```

### 5. Monitoring and Logging

As the script runs, it will output logs to the console to keep you informed of its activities. Here’s what to expect:

- **Connection Status**: The script will confirm when it successfully connects to the Coreflux MQTT broker and the OpenSearch instance.
- **Published Payloads**: The script will log the payloads that are published to the MQTT broker via MQTT Explorer. These are the payloads it will process and attempt to index in OpenSearch.
- **Indexing Status**: After attempting to index a published payload, the script will log whether the operation was successful or if there was an error.
- **Feedback Status**: The script will also log the status of feedback messages it publishes back to the MQTT broker, indicating the success or failure of indexing operations.

These logs are essential for tracking the script's behavior and ensuring that your data is being processed and stored correctly.

### 6. Graceful Shutdown

The script includes a signal handler to ensure that it can shut down gracefully. If you need to stop the script (for example, by pressing `Ctrl+C`), the following will happen:

1. **Stop the MQTT Loop**: The script will first stop the MQTT client loop to ensure that no further messages are processed or published.
2. **Disconnect from MQTT Broker**: It will properly close the connection to the Coreflux MQTT broker, ensuring that all ongoing processes are completed before disconnecting.
3. **Terminate the Script**: The script will then exit cleanly, displaying a shutdown confirmation message in the console.

This graceful shutdown process is crucial for preventing data loss or corruption, particularly when the script is actively processing and indexing data.

## Conclusion

This script is designed to handle payloads that are published to the Coreflux MQTT broker via MQTT Explorer, processing them and storing the relevant data in an OpenSearch instance on DigitalOcean. By following the steps outlined in this documentation, you can ensure that your IoT data is managed efficiently, from the moment it’s published to when it’s safely stored and indexed.

Make sure to monitor the logs for any issues and use the graceful shutdown feature to avoid potential problems when stopping the script. For further customization or troubleshooting, refer to the official documentation for `paho-mqtt` and `opensearch-py`.
