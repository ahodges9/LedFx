import React, { Component } from 'react'
import { connect } from "react-redux";

import { getSpotifyEnabled, setSpotifyEnabled} from 'frontend/actions'
import { Card, CardContent, Switch } from '@material-ui/core'

export class EnableSpotify extends Component {

    toggleSpotify = () => {
        if (this.props.spotifyEnabled == true) {
            this.props.setSpotifyEnabled(false)
        } else {
            this.props.setSpotifyEnabled(true)
        }
    }

    componentDidMount() {
        this.props.getSpotifyEnabled()
    }

    render() {
        return (
            <Card>
                <CardContent>
                    <h3>Enable Spotify</h3>
                    <Switch 
                        checked={this.props.spotifyEnabled}
                        onChange={() => this.toggleSpotify()}
                    />
                </CardContent>
            </Card>
        )
    }
}

function mapStateToProps(state) {
    const  spotifyEnabled  = state.settings.spotifyEnabled
    return {
      spotifyEnabled
    }
}

const mapDispatchToProps = dispatch => ({
    getSpotifyEnabled: () => dispatch(getSpotifyEnabled()),
    setSpotifyEnabled: (bool) => dispatch(setSpotifyEnabled(bool))
})

export default connect(mapStateToProps, mapDispatchToProps)(EnableSpotify);

