from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class ExperimentSettingForm(FlaskForm):
    experiment_name = StringField('Experiment Name', validators=[DataRequired()])
    person_responsible = StringField('Person Responsible', validators=[DataRequired()])
    experiment_description = TextAreaField('Experiment Description', validators=[DataRequired()])
    number_of_samples = StringField('Number of Samples', validators=[DataRequired()])
    thermomixer_time_s = StringField('Thermomixer Time (s)', validators=[DataRequired()])
    liquid_nitrogen_time_s = StringField('Liquid Nitrogen Time (s)', validators=[DataRequired()])
    number_of_cycles = StringField('Number of Cycles', validators=[DataRequired()])
    additional_notes = TextAreaField('Additional Notes', validators=[DataRequired()])
    submit = SubmitField('Submit')