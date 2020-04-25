import React from "react";
import PropTypes from "prop-types";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import withStyles from "@material-ui/core/styles/withStyles";
import { Line } from "react-chartjs-2";
import Sockette from "sockette";

const styles = (theme) => ({
  content: {
    minWidth: 120,
    maxWidth: "100%",
  },
});

class DeviceVisualizer extends React.Component {
  constructor(props) {
    super(props);

    this.websocketActive = false;
    this.websocketPacketId = 1;
    this.deviceUpdateSubscription = null;
    this.state = {};
  }

  handleMessage = (e) => {
    var messageData = JSON.parse(e.data);

    // Ensure this message is for the current device. This can happen
    // during transistions between devices where the component stays
    // loaded
    if (messageData.device_id != this.props.device.id) {
      return;
    }

    this.setState({ messageData: messageData });
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

  componentDidMount() {
    this.connectWebsocket();
  }

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
    const { classes, device } = this.props;

    var border = 0; //Math.max(5, 800/device.config.pixel_count/5);
    var rw = Math.min(
      (800 - border) / device.config.pixel_count,
      32 - border
    );

    const items = []
  
    if (this.state.messageData) {

    for (var i=0;i<device.config.pixel_count;i++) {
      items.push( <rect
        x={border + i * rw}
        y={border}
        height={rw - border}
        width={rw - border}
        style={{fill: "rgb("+this.state.messageData.pixels[0][i]+","+this.state.messageData.pixels[1][i]+","+this.state.messageData.pixels[2][i]+")"}}
        key={i}
      />)
    }
  }

    return (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 32">
        {items}
      </svg>
    );
  }
}

DeviceVisualizer.propTypes = {
  classes: PropTypes.object.isRequired,
  device: PropTypes.object.isRequired,
};

export default withStyles(styles)(DeviceVisualizer);
