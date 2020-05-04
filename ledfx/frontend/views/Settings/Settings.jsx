import React, { useState, useEffect } from "react";
import { connect } from "react-redux";

import Card from "@material-ui/core/Card";
import CardHeader from "@material-ui/core/CardHeader";
import CardContent from "@material-ui/core/CardContent";
import Grid from "@material-ui/core/Grid";
import InputAdornment from "@material-ui/core/InputAdornment";
import MenuItem from "@material-ui/core/MenuItem";
import FormControl from "@material-ui/core/FormControl";
import Select from "@material-ui/core/Select";
import TextField from "@material-ui/core/TextField";
import Typography from "@material-ui/core/Typography";

import { getAudioDevices, setAudioDevice } from "frontend/actions";

const SettingsView = ({ getAudioDevices, setAudioDevice, settings }) => {
  useEffect(() => {
    getAudioDevices();
  }, []);

  const { audioDevices } = settings;

  return (
    <Grid container direction="row" spacing={4}>
      <Grid item lg={6}>
        {audioDevices && (
          <AudioCard
            audioDevices={audioDevices}
            setAudioDevice={setAudioDevice}
          />
        )}
      </Grid>
    </Grid>
  );
};

const AudioCard = ({ audioDevices, setAudioDevice }) => {
  const activeDeviceIndex = audioDevices["active_device_index"];
  const activeAudioLatency = audioDevices["device_latency"];

  const [selectedIndex, setSelectedIndex] = useState(activeDeviceIndex);
  const [audioLatency, setAudioLatency] = useState(activeAudioLatency);

  return (
    <Card variant="outlined">
      <CardHeader
        title="Audio Device"
        subheader="Audio input for reactive effects. Sound card is better than microphone!"
      />
      <CardContent>
        <Typography variant="subtitle2">
          Current device: {audioDevices.devices[activeDeviceIndex]}
        </Typography>
        <div>
          <FormControl>
            <Select
              id="audio-input-select"
              value={selectedIndex}
              onChange={(e) => {
                setSelectedIndex(e.target.value);
                handleSettingsUpdate();
              }}
              onChange={(e) => {
                var idx = e.target.value;
                setSelectedIndex(idx);
                setAudioDevice(idx, audioLatency);
              }}
            >
              {renderAudioInputSelect(audioDevices.devices)}
            </Select>
          </FormControl>
        </div>
        <div>
          <TextField
            type="number"
            InputProps={{
              min: 0,
              max: 10000,
              endAdornment: (
                <InputAdornment position={"end"}>ms</InputAdornment>
              ),
            }}
            label="Compensate for device latency"
            helperText="If your audio device has a latency (e.g. if using AirPlay or Bluetooth), we can delay processing"
            value={audioLatency}
            onChange={(e) => {
              var latency = e.target.value;
              setAudioLatency(latency);
              setAudioDevice(selectedIndex, latency);
            }}
          />
        </div>
      </CardContent>
    </Card>
  );
};

const renderAudioInputSelect = (audioInputs) => {
  return Object.keys(audioInputs).map((key) => (
    <MenuItem key={key} value={key}>
      {audioInputs[key]}
    </MenuItem>
  ));
};

const mapStateToProps = (state) => ({
  settings: state.settings,
});

const mapDispatchToProps = (dispatch) => ({
  getAudioDevices: () => dispatch(getAudioDevices()),
  setAudioDevice: (index, latency) => dispatch(setAudioDevice(index, latency)),
});

export default connect(mapStateToProps, mapDispatchToProps)(SettingsView);
