import React from "react";
import Grid from "@material-ui/core/Grid";
import Card from "@material-ui/core/Card";
import CardContent from '@material-ui/core/CardContent';
import CardActions from '@material-ui/core/CardActions';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import Button from '@material-ui/core/Button';
import { withStyles } from '@material-ui/core/styles';

import PropTypes from 'prop-types';
import { connect } from 'react-redux'

import { activatePreset } from 'frontend/actions';
import { onMidiIn } from '/Users/vladlenkaveev/Documents/ledfx_dev_branch/ledfx/frontend/views/Settings/midi.js'

const styles = theme => ({ 
    button: {
      margin: theme.spacing.unit,
      float: "right"
    },
    submitControls: {
      margin: theme.spacing.unit,
      display: "block",
      width: "100%"
    },
  
  });

  class MidiView extends React.Component {

    render() {
        const {  activatePreset } = this.props;
        return (
            <Card>
            <CardContent>
              <h3>Presets</h3>
            </CardContent>
            <CardActions>
                <Button id="midibutton"
                  color="primary"
                  size="small"
                  aria-label="Activate"
                  variant = "contained"
                  onClick={() => activatePreset('rainbow')}
                > 
                  Rainbowtest
                </Button>
                <Button id="midibutton2"
                  color="primary"
                  size="small"
                  aria-label="Activate"
                  variant = "contained"
                  onClick={() => activatePreset('off')}
                > 
                  OFF
                </Button>
                <Button id="midibutton3"
                  color="primary"
                  size="small"
                  aria-label="Activate"
                  variant = "contained"
                  onClick={() => activatePreset('beat')}
                > 
                  BEAT
                </Button>
              </CardActions>
          </Card>
        );
      }
    }  

    MidiView.propTypes = {
        classes: PropTypes.object.isRequired,
        preset: PropTypes.object.isRequired,
      };
      
      const mapDispatchToProps = (dispatch) => ({
        activatePreset: (presetId) => dispatch(activatePreset(presetId))
      })
      
      export default  connect(null , mapDispatchToProps)(withStyles(styles)(MidiView));