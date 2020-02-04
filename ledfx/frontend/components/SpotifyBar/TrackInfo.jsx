import React, { Component } from 'react'
import PropTypes from "prop-types";
import { connect } from "react-redux";

import withStyles from "@material-ui/core/styles/withStyles";
import { Grid, Card, CardContent, Typography, Slider, FormControl, FormControlLabel, InputLabel, MenuItem, Select, Checkbox, Button } from '@material-ui/core'

import { addTrigger } from 'frontend/actions';

const apiUrl = window.location.protocol + "//" + window.location.host + "/api";

const styles = theme => ({
    card: {
        display: "flex",
        backgroundSize: "contain",
        width: "80%",
        backgroundColor: '#333333',
        boxShadow: 'none'
    },
    progressSlider: {
        margin: '5vh',
        marginBottom: '2vh',
    },
    content: {
        width: '30%',
        padding: '1px',
    },
    connectedMessage: {
        color: "#FFFFFF"
    },
    trackDescription: {
        height: '100%',
        display: 'flex',
        alignItems: 'start',
        justifyContent: 'center',
        flexDirection: 'column',
        marginLeft: '1vw'
    },
    albumName: {
        margin: 0,
        color: '#FFF'
    },
    songTitle: {
        textAlign: 'center',
        margin: 0,
        color: '#FFFFFF'
    },
    presetMenu: {
        width: '40%',
    },
    presetMenuText: {
        color: '#FFFFFF'
    },
    checkboxText: {
        color: '#FFFFFF',
        size: '4vh'
    },
    button: {
        backgroundColor: '#1ED760',
        paddingTop: '1px',
        paddingBottom: '1px'
    }
})

class TrackInfo extends Component {
    constructor(props) {
        super(props);
        this.state = {
            position: 0,
            paused: false,
            presetsObject: null,
            presetSelect: '',
            positionCheck: false
        }
        fetch(`${apiUrl}/presets`)
            .then((response) => {
                return response.json();
            })
            .then((json) => {
                this.state.presetsObject = json.presets
        })
    };

    handleAddToPreset = (id, triggerSong, triggerPosition) => {
        console.log(id, triggerSong, triggerPosition)
        this.props.dispatch(addTrigger(id, triggerSong, triggerPosition))
    };

    handlePresetChange(e) {
        this.setState({presetSelect: e.target.value})
    }

    handleCheckChange(e) {
        this.setState({positionCheck: e.target.checked})
    }

    render() {
        const {classes, addTrigger} = this.props
        this.handlePresetChange = this.handlePresetChange.bind(this)
        this.handleCheckChange = this.handleCheckChange.bind(this)

        this.state.paused = this.props.songPaused

        if (this.props.songState == null) {
            return (
                <Typography component="h3" className={classes.connectedMessage}>
                    Select "LedFX Window" using Spotify Connect!
                </Typography>      
            )
        } else {
            return (
                <Grid container direction="row" alignItems="center" justify="center" className={classes.playbackGrid}>
                    <Card className={classes.card}>
                        <CardContent className={classes.content}>
                            <div className={classes.trackDescription}>
                                <h4 className={classes.songTitle}>{this.props.songState.name}</h4>
                                <p className={classes.albumName}>{this.props.songState.album.name}</p>
                            </div>
                        </CardContent>
                    </Card>

                    <FormControl style={{display: 'flex', flexDirection: 'row'}}>
                        <InputLabel className={classes.presetMenuText}>Preset</InputLabel>
                        <Select className={classes.presetMenu}
                            value={this.state.presetSelect || ''}
                            onChange={this.handlePresetChange}
                            style={{color: 'white'}}
                        >
                            {renderPresetMenu(this.state.presetsObject)}
                        </Select>
                        <FormControlLabel
                            control={<Checkbox 
                                        style={{color: '#00BCD4'}}
                                        onChange={this.handleCheckChange}
                                    />}
                            label="Song Position"
                            labelPlacement="end"
                            className={classes.presetMenuText}
                        />
                        <Button
                            onClick={() => this.handleAddToPreset(this.state.presetSelect, this.props.songState.name, this.props.songPosition)}
                            className={classes.button}
                            type="submit"
                            variant="contained"
                        >Add</Button>
                    </FormControl>
                </Grid>
            )
        }
    }
}

const renderPresetMenu = (presets) => {

    const availablePresets = Object.keys(presets);

    return availablePresets.map(name => {
        return (
            <MenuItem 
                key={name}
                value={name}
            >
                {name}
            </MenuItem>
        )
    })
} 

TrackInfo
.propTypes = {

  classes: PropTypes.object.isRequired
}

const mapStateToProps = state => ({ 
    presets: state.presets 
  })

export default connect(mapStateToProps, null)(withStyles(styles)(TrackInfo));
