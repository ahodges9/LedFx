import React from "react";
import Grid from "@material-ui/core/Grid";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import CardActions from "@material-ui/core/CardActions";
import MenuItem from "@material-ui/core/MenuItem";
import FormControl from "@material-ui/core/FormControl";
import Select from "@material-ui/core/Select";
import Button from "@material-ui/core/Button";
import Slider from "@material-ui/core/Slider";
import Input from "@material-ui/core/Input";
import Typography from "@material-ui/core/Typography";
import { withStyles } from "@material-ui/core/styles";

import PropTypes from "prop-types";
import { connect } from "react-redux";

import { activatePreset } from "frontend/actions";
import { render } from "react-dom";

const styles = (theme) => ({
  button: {
    margin: theme.spacing.unit,
    float: "right",
  },
  submitControls: {
    margin: theme.spacing.unit,
    display: "block",
    width: "100%",
  },
});

var navigator = require("web-midi-api");
var navigator = require("jzz");
var midi;
var inputs;
var outputs;

class MidiControl extends React.Component {
  constructor(props) {
    super(props);
    this.state = { status: null, midiname: null };
  }

  updateMidi() {
    this.setState(() => {
      return { status: startMidi.status, midiname: midiOutput.midiname };
    });
  }

  render() {
    const { activatePreset } = this.props;
    startMidi();
    return (
      <div>
            <Typography variant="h5" color="inherit">
              Midi Control
            </Typography>
            <h3>Device </h3>
            <CardActions>
              <Button onClick={() => this.updateMidi()}>SET MIDI</Button>
              <Typography>{this.state.midiname}</Typography>
              <ul></ul>
              <Typography>Status: {this.state.status}</Typography>
            </CardActions>
            <h3>Presets</h3>
            <CardActions>
              <Button
                id="midibutton"
                color="primary"
                size="small"
                aria-label="Activate"
                variant="contained"
                onClick={() => activatePreset("rainbow")}
              >
                Rainbow
              </Button>
              <Button
                id="midibutton2"
                color="primary"
                size="small"
                aria-label="Activate"
                variant="contained"
                onClick={() => activatePreset("off")}
              >
                OFF
              </Button>
              <Button
                id="midibutton3"
                color="primary"
                size="small"
                aria-label="Activate"
                variant="contained"
                onClick={() => activatePreset("strobe")}
              >
                STROBE
              </Button>
              <ul></ul>
              <Typography id="range-slider" gutterBottom>
                Brightness
              </Typography>
              <ul></ul>
              <Slider
                id="midislider"
                defaultValue={0.5}
                aria-labelledby="discrete-slider"
                valueLabelDisplay="auto"
                step={0.1}
                marks
                min={0}
                max={1}
              ></Slider>
            </CardActions>
      </div>
    );
  }
}

function startMidi() {
  if (navigator.requestMIDIAccess) {
    console.log("WebMIDI is supported in this browser.");
    startMidi.status = "WebMIDI is supported in this browser.";
  } else {
    console.log("WebMIDI is not supported in this browser.");
    startMidi.status = "WebMIDI is not supported in this browser.";
  }
}

function onMIDIFailure(msg) {
  console.log("Failed to get MIDI access - " + msg);
  process.exit(1);
}

function onMIDISuccess(midiAccess) {
  midi = midiAccess;
  inputs = midi.inputs;
  outputs = midi.outputs;
  setTimeout(midiOutput, 500);
}

function midiOutput() {
  console.log("Testing MIDI-Out ports...");
  outputs.forEach(function (port) {
    console.log(
      "id:",
      port.id,
      "manufacturer:",
      port.manufacturer,
      "name:",
      port.name,
      "version:",
      port.version
    );
    midiOutput.midiname = port.name;
    port.open();
    port.send([0x90, 60, 0x7f]);
  });
  setTimeout(stopOutputs, 1000);
}

function stopOutputs() {
  outputs.forEach(function (port) {
    port.send([0x80, 60, 0]);
  });
  testInputs();
}

function onMidiIn(ev) {
  var arr = [];
  for (var i = 0; i < ev.data.length; i++) {
    arr.push((ev.data[i] < 16 ? "0" : "") + ev.data[i].toString(16));
  }
  console.log("MIDI:", arr.join(" "));
  if (arr[0] == 97 && arr[1] == 0 && arr[2] != 0) {
    console.log("One");
    const button = document.querySelector("#midibutton");
    button.click();
  }
  if (arr[0] == 97 && arr[1] == 1 && arr[2] != 0) {
    console.log("Two");
    const button = document.querySelector("#midibutton2");
    button.click();
  }
  if (arr[0] == 97 && arr[1] == 2 && arr[2] != 0) {
    console.log("Three");
    const button = document.querySelector("#midibutton3");
    button.click();
  }
  if (arr[0] == "b0" && arr[1] == 13 && arr[0] != 0) {
    console.log("Four");
  }
}

function testInputs() {
  console.log("Testing MIDI-In ports...");
  inputs.forEach(function (port) {
    console.log("id:", port.id);
    port.onmidimessage = onMidiIn;
  });
}

MidiControl.propTypes = {
  classes: PropTypes.object.isRequired,
  preset: PropTypes.object.isRequired,
};

const mapDispatchToProps = (dispatch) => ({
  activatePreset: (presetId) => dispatch(activatePreset(presetId)),
});

navigator.requestMIDIAccess().then(onMIDISuccess, onMIDIFailure);

export default connect(
  null,
  mapDispatchToProps
)(withStyles(styles)(MidiControl));
