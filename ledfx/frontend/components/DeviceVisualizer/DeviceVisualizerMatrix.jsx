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

class DeviceVisualizerMatrix extends React.Component {
  drawData = (messageData) => {
    // Ensure this message is for the current device. This can happen
    // during transistions between devices where the component stays
    // loaded
    if (messageData.device_id != this.props.device.id) {
      return;
    }

    var rw = Math.min(this.canvas.width / this.props.device.config.width, 
      this.canvas.height / this.props.device.config.height);

    var offset = 0;
    for (var y = 0; y < this.props.device.config.height; y++) {
      for (var x = 0; x < this.props.device.config.width; x++) {
        this.ctx.fillStyle = RGBToHex(
          messageData.pixels[0][offset],
          messageData.pixels[1][offset],
          messageData.pixels[2][offset]
        );

        this.ctx.fillRect(x * rw, y * rw, rw, rw);
        offset++;
      }
    }
  };

  componentDidMount() {
    this.canvas = this.refs.canvas;
    this.ctx = this.canvas.getContext("2d");
  }

  render() {
    const { device } = this.props;
    //const height = Math.ceil((device.height / device.width) * 100) + "%";
    return <canvas ref="canvas" style={{ width: "100%", height: "100%" }} />;
  }
}

DeviceVisualizerMatrix.propTypes = {
  classes: PropTypes.object.isRequired,
  device: PropTypes.object.isRequired,
};

export default withStyles(styles)(DeviceVisualizerMatrix);
