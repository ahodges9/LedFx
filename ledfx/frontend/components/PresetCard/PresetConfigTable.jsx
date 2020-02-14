import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';

import Table from '@material-ui/core/Table';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import TableBody from '@material-ui/core/TableBody';
import Button from '@material-ui/core/Button';
import DeleteIcon from '@material-ui/icons/Delete';
import { deleteTrigger } from '../../actions/presets';
import { connect } from 'react-redux';

const styles = theme => ({
    table: {
    },
    tableHead: {
      fontWeight: 'bold'
    }
});

class PresetConfigTable extends React.Component {

  render() {
    const { deleteTrigger, classes, presetID, devices, triggers } = this.props;

    return (
      <div>
        <Table className = { classes.table }>
          <TableHead>
            <TableRow>
              <TableCell className={classes.tableHead}>Device</TableCell>
              <TableCell className={classes.tableHead}>Effect</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {renderRows(devices)}
          </TableBody>
        </Table>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell className={classes.tableHead}>
                Preset Triggers
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody> 
            {renderTriggers(presetID, triggers, deleteTrigger)}
          </TableBody>
        </Table>
      </div>
    );
  }
}

const renderTriggers = (presetID, triggers, deleteTrigger) => {
  return Object.keys(triggers).map(id => {
    return (
      <TableRow>
        <TableCell>
          {triggers[id][1]}
        </TableCell>
        <TableCell>
          Position: {triggers[id][2]}
        </TableCell>
        <TableCell>
          <Button style={{width: '4vw', backgroundColor: 'red'}} variant='contained' size='small' onClick={() => deleteTrigger(presetID, id)}>
            <DeleteIcon style={{color: '#f1f1f1'}}/>
          </Button>
        </TableCell>
      </TableRow>
    )
  })
}

const renderRows = (devices) => {
  const devicesWithEffects = Object.keys(devices).filter(id => !!devices[id].type);
  return devicesWithEffects.map(id => {
    return (
      <TableRow key={id}>
          <TableCell>
            {id}
          </TableCell>
          <TableCell>
            {devices[id].type}
          </TableCell>
      </TableRow>
    )})
}

PresetConfigTable.propTypes = {
  classes: PropTypes.object.isRequired,
  devices: PropTypes.object.isRequired
};

const mapStateToProps = state => ({
  ttriggers: state.triggers
})

const mapDispatchToProps = (dispatch) => ({
  deleteTrigger: (presetID, id) => dispatch(deleteTrigger(presetID, id)),
})

export default connect(mapStateToProps, mapDispatchToProps)(withStyles(styles)(PresetConfigTable));