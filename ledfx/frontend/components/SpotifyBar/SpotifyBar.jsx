import React, { Component } from 'react'
import PropTypes from "prop-types";
import { connect } from "react-redux";

import withStyles from "@material-ui/core/styles/withStyles";
import { AppBar, Button, Grid } from '@material-ui/core';
import {drawerWidth} from "frontend/assets/jss/style.jsx";
import TrackInfo from './TrackInfo';

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
        console.log(accessToken)
        return this.setState({
            token: accessToken
        }) 
    }

    initializePlayer() {
        window.onSpotifyWebPlaybackSDKReady = () => {
            const token = this.state.token;
            const player = new Spotify.Player({
                name: 'LedFX Window',
                getOAuthToken: cb => {  
                    cb(token);  
                }
            });
          
            player.addListener('initialization_error', ({ message }) => { console.error(message) });
            player.addListener('authentication_error', ({ message }) => { console.error(message) });
            player.addListener('account_error', ({ message }) => { console.error(message) });
            player.addListener('playback_error', ({ message }) => { console.error(message) });
            player.addListener('ready', ({ device_id }) => {console.log('Ready with Device ID', device_id)});
            player.addListener('not_ready', ({ device_id }) => {console.log('Device ID has gone offline', device_id)});

            player.addListener('player_state_changed', state => { this.handlePlayerStateChange(state) });

            player.connect();
        }
    }

    handlePlayerStateChange(state) {
        this.setState({playbackState: state.track_window.current_track})
        console.log(this.state.playbackState)
        return 
    }

    componentDidMount() {

        this.getAccessToken();
        console.log(this.state.token, "inside did mount")
        this.initializePlayer();
    }

    render() {
        const {classes} = this.props;
        console.log(this.state.token, 'inside render')
        if (this.state.token === "") {
            return (
                <AppBar className={classes.appBar}>
                    <Grid container direction="row" justify="space-evenly" alignItems="center">
                        <Grid item xs>
                            <Button  variant="contained" style={{backgroundColor: '#1ED760', color: '#FFFFFA'}}className={classes.spotifyLogin} onClick={this.spotifyLogin}>Log in with Spotify</Button>
                        </Grid>
                    </Grid>
                </AppBar>
            )
        } else {
            return (
                <AppBar className={classes.appBar}>
                    <Grid container direction="row" justify="space-evenly" alignItems="center">
                        <Grid item xs>
                            <TrackInfo />
                        </Grid>
                    </Grid>
                </AppBar>
            )
        }   
    }
}

SpotifyBar.propTypes = {
  classes: PropTypes.object.isRequired
}
export default connect(null,null)(withStyles(styles)(SpotifyBar));
