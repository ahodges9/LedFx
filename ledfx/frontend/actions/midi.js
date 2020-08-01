var navigator = require('web-midi-api');
// consider using var navigator = require('jzz');

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
  setTimeout(testOutputs, 500);
}

function testOutputs(index){
  const data = {
    index: parseInt(index)
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
  setTimeout(stopInputs, 5000);
}

navigator.requestMIDIAccess().then(onMIDISuccess, onMIDIFailure);