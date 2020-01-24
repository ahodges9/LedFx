import React, { Component } from 'react'
import PropTypes from "prop-types";
import { connect } from "react-redux";
import fetch from "cross-fetch";

import withStyles from "@material-ui/core/styles/withStyles";
import { AppBar, Button, Grid } from '@material-ui/core';
import {drawerWidth} from "frontend/assets/jss/style.jsx";
import TrackInfo from './TrackInfo';

import activatePreset from 'frontend/actions';

const apiUrl = window.location.protocol + "//" + window.location.host + "/api";

const styles = theme => ({
    appBar: {
        backgroundColor: '#333333',
        top: 'auto',
        bottom: 0,
        [theme.breakpoints.up('md')]: {
            marginLeft: drawerWidth,
            width: `calc(100% - ${drawerWidth}px)`
        }
    },
    spotifyLogin : {
        color:  '#333333'
    }
})

class SpotifyBar extends Component {

    state = {
        token: null,
        playbackState: null
    }
    

    spotifyLogin() {
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

            // Listen
            player.addListener('player_state_changed', state => { this.handlePlayerStateChange(state) });

            player.connect();
        }
    }


    handlePlayerStateChange(state) {
        this.setState({playbackState: state.track_window.current_track})

        fetch(`${apiUrl}/presets`)
            .then((response) => {
                return response.json();
            })
            .then((json) => {
                let allPresets = Object.entries(json.presets);
                allPresets.forEach(element => {
                    if (element[1].triggerSongs) {
                        if (element[1].triggerSongs == this.state.playbackState.name){
                            
                            console.log('current track matches preset for:', element[1].name )
                            const data = {
                                id: element[1].id,
                                action: 'activate'
                              };
                              fetch(`${apiUrl}/presets`, {
                                method: "PUT",
                                headers: {
                                  Accept: "application/json",
                                  "Content-Type": "application/json"
                                },
                                body: JSON.stringify(data)
                              })                         
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
        const {classes, activatePreset} = this.props;
        if (this.state.token === "") {
            return (
                <AppBar className={classes.appBar}>
                    <Grid container direction="row" justify="center" alignItems="center">
                        <Button  variant="contained" style={{backgroundColor: '#1ED760', color: '#FFFFFA'}}className={classes.spotifyLogin} onClick={this.spotifyLogin}>Log in with Spotify</Button>   
                    </Grid>
                </AppBar>
            )
        } else {
            return (
                <AppBar className={classes.appBar}>
                    <Grid container direction="row" justify="center" alignItems="center">  
                        <TrackInfo />
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
