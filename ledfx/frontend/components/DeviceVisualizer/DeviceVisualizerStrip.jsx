import React from "react";
import PropTypes from "prop-types";
import withStyles from "@material-ui/core/styles/withStyles";
import { RGBToHex } from 'frontend/utils/helpers';

const styles = (theme) => ({
  content: {
    minWidth: 120,
    maxWidth: "100%",
  },
});

class DeviceVisualizerStrip extends React.Component {
  
  drawData = (messageData) => {
    // Ensure this message is for the current device. This can happen
    // during transistions between devices where the component stays
    // loaded
    if (messageData.device_id != this.props.device.id) {
      return;
    }

    var rw = this.canvas.width / this.props.device.config.pixel_count;

    for (var i = 0; i < this.props.device.config.pixel_count; i++) {
      this.ctx.fillStyle = RGBToHex(
        messageData.pixels[0][i],
        messageData.pixels[1][i],
        messageData.pixels[2][i]
      );

      this.ctx.fillRect(i * rw, 0, rw, this.canvas.height);
    }
  };

  componentDidMount() {
    this.canvas = this.refs.canvas;
    this.ctx = this.canvas.getContext("2d");
  }

  render() {
    return <canvas ref="canvas" style={{ width: "100%", height: 10 }} />;
  }
}

DeviceVisualizerStrip.propTypes = {
  classes: PropTypes.object.isRequired,
  device: PropTypes.object.isRequired,
};

export default withStyles(styles)(DeviceVisualizerStrip);
