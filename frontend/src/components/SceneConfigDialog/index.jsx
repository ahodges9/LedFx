import React from 'react';
import withStyles from '@material-ui/core/styles/withStyles';
import { connect } from 'react-redux';

import Dialog from '@material-ui/core/Dialog';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContentText from '@material-ui/core/DialogContentText';

import SchemaFormCollection from 'components/SchemaForm';
import { addDevice } from 'actions';

const styles = theme => ({
    button: {
        float: 'right',
    },
});

class SceneConfigDialog extends React.Component {
    handleClose = () => {
        this.props.onClose();
    };

    handleSubmit = (type, config) => {
        this.props.dispatch(addDevice(type, config));
        this.props.onClose();
    };

    render() {
        const { classes, dispatch, schemas, onClose, ...otherProps } = this.props;
        return (
            <Dialog
                onClose={this.handleClose}
                className={classes.cardResponsive}
                aria-labelledby="form-dialog-title"
                {...otherProps}
            >
                <DialogTitle id="form-dialog-title">Add QLC+ Widget</DialogTitle>
                <DialogContent className={classes.cardResponsive}>
                    <DialogContentText>
                        Once you have created your widgets in QLC+ API, and QLC+ currently in live mode,
                        you can select from your QLC+ Widget list. NOTES: Backend QLC API get WidgetsList.
                    </DialogContentText>
                    <SchemaFormCollection
                        schemaCollection={schemas.devices}
                        onSubmit={this.handleSubmit}
                        useAdditionalProperties={true}
                        submitText="Add"
                        onCancel={this.handleClose}
                        //Once selected a Widget option, Value text will say:
                        
                        //The value to set depends on the widget type itself. 
                        //Buttons will only support values 255 (= button is pressed) 
                        //and 0 (= button is released), 
                        //Audio triggers will support values 0 (= off) and 255 (= on)
                        // and Sliders will accept all the values in the 0-255 range.
                    />
                </DialogContent>
            </Dialog>
        );
    }
}

export default connect(state => ({
    schemas: state.schemas,
}))(withStyles(styles)(SceneConfigDialog));
