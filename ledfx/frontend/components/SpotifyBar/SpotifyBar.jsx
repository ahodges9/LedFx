import React, { Component } from 'react'
import PropTypes from "prop-types";
import { connect } from "react-redux";
import fetch from "cross-fetch";

import withStyles from "@material-ui/core/styles/withStyles";
import { AppBar, Button, Grid } from '@material-ui/core';
import {drawerWidth} from "frontend/assets/jss/style.jsx";
import TrackInfo from './TrackInfo';

import {activatePreset} from 'frontend/actions';
import { AddTrigger } from './AddTrigger';

const apiUrl = window.location.protocol + "//" + window.location.host + "/api";

const styles = theme => ({
    appBar: {
        backgroundColor: '#333333',
        top: 'auto',
        bottom: 0,   
        boxShadow: 'none',
        [theme.breakpoints.up('md')]: {
            left: `calc(${drawerWidth}px - 2px)`,
            width: `calc(100% - ${drawerWidth}px + 1vw)`
        }
    },
    loginBar: {
        paddingTop: '2vh',
        paddingBottom: '2vh'
    },
    spotifyLogin : {
        color:  '#333333',
    }
})

class SpotifyBar extends Component {
    constructor(props) {
        super(props);
        this.state = {
            token: null,
            trackState: null,
            trackPosition: 0,
            trackDuration: null,
            trackPaused: true
        }
    }
    

    spotifyLogin() {
        // Basically just send them to the Spotify login page with required scopes and our app ID
        let scopes = encodeURIComponent('streaming user-read-email user-read-private');
        let client_id = 'a4d6df0f4b0047c2b23216c46bfc0f27'
        let redirect_uri = 'http://127.0.0.1:8888/dashboard/'
        
        window.location = [
            "https://accounts.spotify.com/authorize",
            `?client_id=${client_id}`,
            `&redirect_uri=${redirect_uri}`,
            `&scope=${scopes}`,
            "&response_type=token",
            "&show_dialog=true"
      ].join('');
    }

    getAccessToken() {
        // Grab the access token from Spotify after completing Spotify login
        var hash = window.location.hash.substr(1)
        console.log(hash)
        const accessToken = hash.split('&')[0].slice(13)
        return this.setState({
            token: accessToken
        }) 
    }

    initializePlayer() {
        // Make sure the 3rd-party Spotify script has loaded 
        window.onSpotifyWebPlaybackSDKReady = () => {
            const token = this.state.token;
            const player = new Spotify.Player({
                name: 'LedFX Window',
                getOAuthToken: cb => {  
                    cb(token);  
                }
            });

            // Set up the web player
            player.addListener('initialization_error', ({ message }) => { console.error(message) });
            player.addListener('authentication_error', ({ message }) => { console.error(message) });
            player.addListener('account_error', ({ message }) => { console.error(message) });
            player.addListener('playback_error', ({ message }) => { console.error(message) });
            player.addListener('ready', ({ device_id }) => {console.log('Ready with Device ID', device_id)});
            player.addListener('not_ready', ({ device_id }) => {console.log('Device ID has gone offline', device_id)});

            // Listen for currently playing song changes
            player.addListener('player_state_changed', state => { this.handlePlayerStateChange(state) });

            player.connect();
        }
    }


    handlePlayerStateChange(state) {
        // Set playback state to a Spotify WebPlaybackTrack -> https://developer.spotify.com/documentation/web-playback-sdk/reference/#object-web-playback-track
        this.setState({trackState: state.track_window.current_track})
        this.setState({trackPosition: state.position})
        this.setState({trackPaused: state.paused})

        console.log(state.position)

        // Fetch duration of current song. Web player doesn't provide this, so we need to use the Spotify Web API.
        fetch(`https://api.spotify.com/v1/tracks?ids=${this.state.trackState.id}`, {
            headers: {
                'Authorization': `Bearer ${this.state.token}` 
            }
        })
        .then((response) => {
            return response.json();
        })
        .then((json) => {
            this.state.trackDuration = json.tracks[0].duration_ms
        })

        // Fetch all presets
        fetch(`${apiUrl}/presets`)
            .then((response) => {
                return response.json();
            })
            .then((json) => {

                // Turn the presets object into a bunch of arrays
                let allPresets = Object.entries(json.presets);

                // Loop through the presets and look for a match between trigger songs and current playback song
                allPresets.forEach(element => {
                    if (element[1].triggerSongs) {
                        if (element[1].triggerSongs == this.state.trackState.name){
                            this.props.activatePreset(element[1].id)                        
                        }
                    }
                })
        });
        return 
    }

    componentDidMount() {
        this.getAccessToken();
        this.initializePlayer();
    }

    render() {
        const {classes} = this.props;

        if (this.state.token === "") {
            return (
                <AppBar className={classes.appBar}>
                    <Grid container direction="row" justify="center" alignItems="center" className={classes.loginBar}>
                        <Button  variant="contained" style={{backgroundColor: '#1ED760', color: '#FFFFFA'}}className={classes.spotifyLogin} onClick={this.spotifyLogin}>Log in with Spotify</Button>   
                    </Grid>
                </AppBar>
            )
        } else {
            return (
                <AppBar className={classes.appBar}>
                    <Grid container direction="row" justify="center" alignItems="center">  
                        <AddTrigger />
                    </Grid>
                </AppBar>
            )
        }   
    }
}

SpotifyBar.propTypes = {
  classes: PropTypes.object.isRequired
}

const mapDispatchToProps = (dispatch) => ({
    activatePreset: (presetId) => dispatch(activatePreset(presetId))
})

export default connect(null, mapDispatchToProps)(withStyles(styles)(SpotifyBar));
