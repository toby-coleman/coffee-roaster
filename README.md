# Basic Raspberry Pi Image

Runs on [Balena](https://www.balena.io/).

## Services

### Node-RED

See [here](https://github.com/balena-io-projects/balena-node-red) for more information. The following environment variables must be configured:

Variable Name | Default       | Description
------------- | ------------- | -------------
PORT          | `8080`        | the port that exposes the Node-RED UI
USERNAME      | `none`        | the Node-RED admin username
PASSWORD      | `none`        | the Node-RED admin password [hash](https://nodered.org/docs/security#generating-the-password-hash)

You **must** set the `USERNAME` and `PASSWORD` environment variables to be able to save or run programs in Node-RED. 

### Redis

Provides a cache for use by the other components.

### Dash app

Basic template of a [Dash](https://plot.ly/products/dash/) UI.
