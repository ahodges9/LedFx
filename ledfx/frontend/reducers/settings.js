import {
    GET_AUDIO_INPUTS,
    SET_AUDIO_INPUT,
    GET_SPOTIFY_ENABLED
} from 'frontend/actions'

export function settings(state = {}, action) {
    console.log(action)
    switch (action.type) {
        case GET_AUDIO_INPUTS:
            const audioDevices = action.audioDevices
            return {...state, audioDevices}
        case GET_SPOTIFY_ENABLED:
            const spotifyEnabled = action.spotifyEnabled 
            return {...state, spotifyEnabled}
        default:
            return state
    }
}