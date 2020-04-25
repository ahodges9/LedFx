import React from "react";
import PropTypes from "prop-types";
import withStyles from "@material-ui/core/styles/withStyles";
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

    var rw = this.refs.canvas.width / this.props.device.config.pixel_count;

    for (var i = 0; i < this.props.device.config.pixel_count; i++) {
      this.ctx.fillStyle = this.RGBToHex(
        messageData.pixels[0][i],
        messageData.pixels[1][i],
        messageData.pixels[2][i]
      );

      this.ctx.fillRect(i * rw, 0, rw, this.refs.canvas.height);
    }
  };

  RGBToHex = (r, g, b) => {
    r = Math.round(r).toString(16);
    g = Math.round(g).toString(16);
    b = Math.round(b).toString(16);

    if (r.length == 1) r = "0" + r;
    if (g.length == 1) g = "0" + g;
    if (b.length == 1) b = "0" + b;

    return "#" + r + g + b;
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
    const canvas = this.refs.canvas;
    this.ctx = canvas.getContext("2d");
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

    return <canvas ref="canvas" style={{ width: "100%", height: 10 }} />;
  }
}

DeviceVisualizer.propTypes = {
  classes: PropTypes.object.isRequired,
  device: PropTypes.object.isRequired,
};

export default withStyles(styles)(DeviceVisualizer);
