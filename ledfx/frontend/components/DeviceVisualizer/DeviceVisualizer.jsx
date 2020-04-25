import React from "react";
import PropTypes from "prop-types";
import Sockette from "sockette";
import DeviceVisualizerMatrix from "./DeviceVisualizerMatrix";

class DeviceVisualizer extends React.Component {
  constructor(props) {
    super(props);

    this.websocketActive = false;
    this.websocketPacketId = 1;
    this.deviceUpdateSubscription = null;
    this.state = {};
  }

  componentDidMount() {
    this.connectWebsocket();
  }
  handleMessage = (e) => {
    var messageData = JSON.parse(e.data);
    this.refs.vis.drawData(messageData);
  };

  handleOpen = (e) => {
    this.enablePixelVisualization(this.props.device);
    this.websocketActive = true;
  };

  handleClose = (e) => {
    this.websocketActive = false;
  };

  enablePixelVisualization = (device) => {
    this.state.ws.json({
      id: this.websocketPacketId,
      type: "subscribe_event",
      event_type: "device_update",
      event_filter: { device_id: device.id },
    });
    this.deviceUpdateSubscription = this.websocketPacketId;
    this.websocketPacketId++;
  };

  disablePixelVisualization = () => {
    this.state.ws.json({
      id: this.websocketPacketId,
      type: "unsubscribe_event",
      subscription_id: this.deviceUpdateSubscription,
    });
    this.deviceUpdateSubscription = null;
    this.websocketPacketId++;
  };

  connectWebsocket = () => {
    const websocketUrl = "ws://" + window.location.host + "/api/websocket";
    const ws = new Sockette(websocketUrl, {
      timeout: 5e3,
      maxAttempts: 10,
      onopen: this.handleOpen,
      onmessage: this.handleMessage,
      onclose: this.handleClose,
      onerror: (e) => console.log("WebSocket Error:", e),
    });

    this.setState({ ws: ws });
  };

  disconnectWebsocket = () => {
    if (this.state.ws != undefined && this.websocketActive) {
      this.state.ws.close(1000);
      this.setState({ ws: undefined });
    }
  };

  componentWillUnmount() {
    this.disconnectWebsocket();
  }

  componentWillReceiveProps(nextProps) {
    if (this.websocketActive) {
      this.disablePixelVisualization();
      this.enablePixelVisualization(nextProps.device);
    }
  }

  render() {
    const { device } = this.props;

    return <DeviceVisualizerMatrix device={device} ref="vis" />;
  }
}

DeviceVisualizer.propTypes = {
  device: PropTypes.object.isRequired,
};

export default DeviceVisualizer;
