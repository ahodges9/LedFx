import { combineReducers } from 'redux'
import { devicesById } from './devices'
import { schemas } from './schemas'
import { presets } from './presets'
import { settings } from './settings'

const rootReducer = combineReducers({
    devicesById,
    schemas,
    presets,
    settings
})

export default rootReducer