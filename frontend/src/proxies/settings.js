import { api } from 'utils/api';

export function getSystemConfig() {
    return api.get('/config');
}

export function getAudioInputs() {
    return api.get('/audio/devices');
}
export function updateSelectedAudioInput(data) {
    return api.put('/audio/devices', data);
}

export function getQLCEnabled(data) {
    return api.get('/qlc', data);
}
export function setQLCEnabled(data) {
    return api.put('/qlc', data);
}
