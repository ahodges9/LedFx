var navigator = require('web-midi-api');
const apiUrl = window.location.protocol + "//" + window.location.host + "/api";

var midi;
var inputs;
var outputs;

export const GET_AUDIO_INPUTS = "GET_AUDIO_INPUTS"
export const SET_AUDIO_INPUT = "GET_AUDIO_INPUT"

export function setAudioDevice(index) {
  return dispatch => {
    const data = {
      index: parseInt(index)
    };
    fetch(`${apiUrl}/audio/devices`, {
      method: "PUT",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    })
      .then(response => response.json())
      .then(json => dispatch({
        type: SET_AUDIO_INPUT,
        response: json
      }))
      .then(() => dispatch(getAudioDevices()));
  };
}


export function getAudioDevices() {
  return dispatch => {
    fetch(`${apiUrl}/audio/devices`, {
      method: "GET",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
    })
      .then(response => response.json())
      .then(json => dispatch({
          type: GET_AUDIO_INPUTS,
          audioDevices: json,
          receivedAt: Date.now()
      }))
  }
}

function onMIDIFailure(msg){
  console.log('Failed to get MIDI access - ' + msg);
  process.exit(1);
}

function onMIDISuccess(midiAccess){
  midi = midiAccess;
  inputs = midi.inputs;
  outputs = midi.outputs;
  setTimeout(testOutputs, 500);
}

function testOutputs(index1){
  const data = {
    index: parseInt(index1)
  };
  console.log('Testing MIDI-Out ports...');
  outputs.forEach(function(port){
    console.log('name:', port.name);
    port.open();
    port.send([0x90, 60, 0x7f]);
  });
  setTimeout(stopOutputs, 1000);
}

function stopOutputs(){
  outputs.forEach(function(port){
    port.send([0x80, 60, 0]);
  });
  testInputs();
}

function onMidiIn(ev){
  var arr = [];
  for(var i = 0; i < ev.data.length; i++){
    arr.push((ev.data[i] < 16 ? '0' : '') + ev.data[i].toString(16));
  }
  console.log('MIDI:', arr.join(' '));
}

function testInputs(){
  console.log('Testing MIDI-In ports...');
  inputs.forEach(function(port){
    console.log('id:', port.id);
    port.onmidimessage = onMidiIn;
  });
}

navigator.requestMIDIAccess().then(onMIDISuccess, onMIDIFailure);