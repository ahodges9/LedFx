import React, { Component } from 'react'
import PropTypes from "prop-types";
import { connect } from "react-redux";

import withStyles from "@material-ui/core/styles/withStyles";
import { Grid, Card, CardContent, Typography, CardMedia } from '@material-ui/core'

const styles = theme => ({
    card: {
        display: "flex",
        backgroundSize: "contain",
        width: "100%"
    },
    albumArt: {
        height: "7vh",
        width: "7vh"
    }
})
class TrackInfo extends Component {
    render() {
        const {classes} = this.props

        return (
            <Grid container direction="row" alignItems="center" justify="center" >
                <Card className={classes.card}>
                    <CardMedia className={classes.albumArt}
                        image="https://picsum.photos/200/300"                      
                    />
                    <CardContent className={classes.content}>
                        <Typography component="h7" variant="h7">
                            Song Title
                        </Typography>
                        <Typography variant="subtitle2" color="textSecondary">
                            Album Title
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>
        )
    }
}

TrackInfo
.propTypes = {
  classes: PropTypes.object.isRequired
}

export default connect(null,null)(withStyles(styles)(TrackInfo));
