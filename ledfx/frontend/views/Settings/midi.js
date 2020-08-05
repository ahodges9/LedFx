import activatePreset from '/Users/vladlenkaveev/Documents/ledfx_dev_branch/ledfx/frontend/actions/presets.js'
import Button from '@material-ui/core/Button';
import PresetCard from '/Users/vladlenkaveev/Documents/ledfx_dev_branch/ledfx/frontend/components/PresetCard/PresetCard.jsx'

var navigator = require('web-midi-api');
var navigator = require('jzz');

var midi;
var inputs;
var outputs;

function onMIDIFailure(msg){
  console.log('Failed to get MIDI access - ' + msg);
  process.exit(1);
}

function onMIDISuccess(midiAccess){
  midi = midiAccess;
  inputs = midi.inputs;
  outputs = midi.outputs;
  setTimeout(midiOutput, 500);
}

function midiOutput(){
  console.log('Testing MIDI-Out ports...');
  outputs.forEach(function(port){
    console.log('id:', port.id, 'manufacturer:', port.manufacturer, 'name:', port.name, 'version:', port.version);
    port.open();
    port.send([0x90, 60, 0x7f]);
    var min = port.name;
    document.getElementById("port").innerHTML = min;
    
    return port.name
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
  if (arr[0] == 97 && arr[1] == 0 && arr[2] != 0)
  {
    console.log('One')
    const button = document.querySelector('#midibutton');
    button.click();
  }
  if (arr[0] == 97 && arr[1] == 1 && arr[2] != 0)
  {
    console.log('Two')
    const button = document.querySelector('#midibutton2');
    button.click();
  }
  if (arr[0] == 97 && arr[1] == 2 && arr[2] != 0)
  {
    console.log('Three')
    const button = document.querySelector('#midibutton3');
    button.click();
  }
  
}

function testInputs(){
  console.log('Testing MIDI-In ports...');
  inputs.forEach(function(port){
    console.log('id:', port.id);
    port.onmidimessage = onMidiIn;
  });
}

export default midiOutput;
navigator.requestMIDIAccess().then(onMIDISuccess, onMIDIFailure);