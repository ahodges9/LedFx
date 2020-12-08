import React, { Component } from 'react'
import { connect } from "react-redux";

import { getQLCEnabled, setQLCEnabled} from 'frontend\src\proxies'
import { Card, CardContent, Switch } from '@material-ui/core'


export class EnableQLC extends Component {

    toggleQLC = () => {
        if (this.props.QLCEnabled == true) {
            this.props.setQLCEnabled(false)
        } else {
            this.props.setQLCEnabled(true)
        }
    }

    componentDidMount() {
        this.props.getQLCEnabled()
    }

    render() {
        return (
            <Card>
                <CardContent>
                    <h3>Enable QLC+ Server</h3>
                    <Switch 
                        checked={this.props.QLCEnabled}
                        onChange={() => this.toggleQLC()}
                    />
                </CardContent>
            </Card>
        )
    }
}

function mapStateToProps(state) {
    const  QLCEnabled  = state.settings.QLCEnabled
    return {
      QLCEnabled
    }
}

const mapDispatchToProps = dispatch => ({
    getQLCEnabled: () => dispatch(getQLCEnabled()),
    setQLCEnabled: (bool) => dispatch(setQLCEnabled(bool))
})

export default connect(mapStateToProps, mapDispatchToProps)(EnableQLC);

