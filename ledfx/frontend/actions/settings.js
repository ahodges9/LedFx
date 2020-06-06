const apiUrl = window.location.protocol + "//" + window.location.host + "/api";

export const GET_AUDIO_INPUTS = "GET_AUDIO_INPUTS"
export const SET_AUDIO_INPUT = "GET_AUDIO_INPUT"
export const GET_SPOTIFY_ENABLED = "GET_SPOTIFY_ENABLED"
export const SET_SPOTIFY_ENABLED = "SET_SPOTIFY_ENABLED"

export function setAudioDevice(index) {
  return dispatch => {
    const data = {
      index: parseInt(index)
    };
    fetch(`${apiUrl}/audio/devices`, {
      method: "PUT",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    })
      .then(response => response.json())
      .then(json => dispatch({
        type: SET_AUDIO_INPUT,
        response: json
      }))
      .then(() => dispatch(getAudioDevices()));
  };
}


export function getAudioDevices() {
  return dispatch => {
    fetch(`${apiUrl}/audio/devices`, {
      method: "GET",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
    })
      .then(response => response.json())
      .then(json => dispatch({
          type: GET_AUDIO_INPUTS,
          audioDevices: json,
          receivedAt: Date.now()
      }))
  }
}

export function setSpotifyEnabled(bool) {
  return dispatch => {
    const data = {
      spotify_enabled: bool
    };
    fetch(`${apiUrl}/spotify`, {
      method: "PUT",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    })
      .then(response => response.json())
      .then(json => dispatch({
        type: SET_SPOTIFY_ENABLED,
        response: json
      }))
      .then(() => dispatch(getSpotifyEnabled()));
  };
}


export function getSpotifyEnabled() {
  return dispatch => {
    fetch(`${apiUrl}/spotify`, {
      method: "GET",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
    })
      .then(response => response.json())
      .then(json => dispatch({
          type: GET_SPOTIFY_ENABLED,
          spotifyEnabled: json,
          receivedAt: Date.now()
      }))
  }
}
