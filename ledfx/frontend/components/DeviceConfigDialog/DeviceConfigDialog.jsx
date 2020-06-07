import React from "react";
import withStyles from "@material-ui/core/styles/withStyles";
import { connect } from "react-redux";

import Button from "@material-ui/core/Button";
import Dialog from "@material-ui/core/Dialog";
import DialogContent from "@material-ui/core/DialogContent";
import DialogTitle from "@material-ui/core/DialogTitle";
import DialogContentText from "@material-ui/core/DialogContentText";

import SchemaFormCollection from "frontend/components/SchemaForm/SchemaFormCollection.jsx";
import { addDevice, updateDevice } from "frontend/actions";

const styles = (theme) => ({
  button: {
    float: "right",
  },
});

class DeviceConfigDialog extends React.Component {
  constructor(props) {
    super(props);
  }

  handleClose = () => {
    this.props.onClose();
  };

  handleSubmit = (type, config, deviceId) => {
    if (deviceId) {
      this.props.dispatch(updateDevice(deviceId, type, config));
    } else {
      this.props.dispatch(addDevice(type, config));
    }
    this.props.onClose();
  };

  render() {
    const {
      classes,
      dispatch,
      schemas,
      onClose,
      initialModel,
      ...otherProps
    } = this.props;
    return (
      <Dialog
        onClose={this.handleClose}
        className={classes.cardResponsive}
        aria-labelledby="form-dialog-title"
        {...otherProps}
      >
        <DialogTitle id="form-dialog-title">
          {!!initialModel ? "Edit Device" : "Add Device"}
        </DialogTitle>
        <DialogContent className={classes.cardResponsive}>
          <DialogContentText>
            To configure a device for LedFx, please first select the type of
            device, then provide the necessary configuration.
          </DialogContentText>
          <SchemaFormCollection
            schemaCollection={schemas.devices}
            onSubmit={(type, config) => {
              this.handleSubmit(type, config, initialModel && initialModel.id);
            }}
            useAdditionalProperties={true}
            initialModel={!!initialModel ? initialModel.config : undefined}
            collectionKey={!!initialModel ? initialModel.type : undefined}
          >
            <Button className={classes.button} type="submit" color="primary">
              Ok
            </Button>
            <Button
              className={classes.button}
              onClick={this.handleClose}
              color="primary"
            >
              Cancel
            </Button>
          </SchemaFormCollection>
        </DialogContent>
      </Dialog>
    );
  }
}

function mapStateToProps(state) {
  const { schemas } = state;

  return {
    schemas,
  };
}

export default connect(mapStateToProps)(withStyles(styles)(DeviceConfigDialog));
