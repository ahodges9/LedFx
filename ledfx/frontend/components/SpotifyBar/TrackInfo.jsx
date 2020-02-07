import React, { Component } from 'react'
import { connect } from "react-redux";

import withStyles from "@material-ui/core/styles/withStyles";
import { Grid } from '@material-ui/core'

import {getPresets, activatePreset} from 'frontend/actions'

const styles = theme => ({
    outer: {
        paddingLeft: '1vw'
    },
    songTitle: {
        color: '#1ED760',
        marginBottom: 2
    },
    albumName: {
        marginTop: 0,
        color: '#1ED760'
    },
    positionText: {
        color: '#1ED760',
        margin: 0
    }
})

class TrackInfo extends Component {
    constructor(props) {
        super(props);
        this.state = {
            trackName: ''
        }
    };

    async checkForTriggers() {
        Object.entries(this.props.presets).forEach((preset) => {
            let presetID = preset[1].name
            let triggersObject = preset[1].triggers
            Object.keys(triggersObject).forEach( (song) => {
                if (this.props.trackState.name == song) {
                    this.props.activatePreset(presetID)
                    console.log('activated', presetID)
                }
            })
        })
    }

    componentDidMount() {
        this.props.getPresets()
    }

    componentDidUpdate() {
        this.checkForTriggers()
    }

    render() {
        const {classes, trackState, position, isPaused} = this.props

        return (
            <Grid container direction='row' className={classes.outer}>
                <Grid item xs='9' container direction='column' justify='center' alignItems='flex-start'>
                    <h4 className={classes.songTitle}>{trackState.name}</h4>
                    <p className={classes.albumName}>{trackState.album.name}</p>
                </Grid> 
                <Grid item xs='3' container direction='column' justify='center' alignItems='flex-end'>
                    <p className={classes.positionText}>Position</p>
                    <p className={classes.positionText}>{position}</p>
                </Grid>
            </Grid>
        )
    }
}

const mapStateToProps = state => ({ 
    presets: state.presets 
})

const mapDispatchToProps = (dispatch) => ({
    getPresets: () => dispatch(getPresets()),
    activatePreset: (id) => dispatch(activatePreset(id))
})

export default connect(mapStateToProps, mapDispatchToProps)(withStyles(styles)(TrackInfo));
