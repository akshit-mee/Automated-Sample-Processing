from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional

class ExperimentSettingForm(FlaskForm):
    experiment_name = StringField('Experiment Name', validators=[DataRequired()])
    person_responsible = StringField('Person Responsible', validators=[DataRequired()])
    experiment_description = TextAreaField('Experiment Description', validators=[DataRequired()])
    number_of_samples = IntegerField('Number of Samples', validators=[DataRequired(), NumberRange(min=1)])
    thermomixer_time_s = IntegerField('Thermomixer Time (s)', validators=[DataRequired(), NumberRange(min=2)])
    liquid_nitrogen_time_s = IntegerField('Liquid Nitrogen Time (s)', validators=[DataRequired(), NumberRange(min=2)])
    waiting_time_s = IntegerField('Waiting Time (s)', validators=[DataRequired(), NumberRange(min=2)])
    number_of_cycles = IntegerField('Number of Cycles', validators=[DataRequired(), NumberRange(min=1)])
    additional_notes = TextAreaField('Additional Notes', validators=[Optional()])
    submit = SubmitField('Save Settings')