from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db

class ExperimentSetting(db.Model):
    __tablename__ = 'experiment_settings'
    
    experiment_id = sa.Column(sa.Integer, primary_key=True)
    experiment_name = sa.Column(sa.String, nullable=False)
    person_responsible = sa.Column(sa.String, nullable=True)
    experiment_description = sa.Column(sa.String, nullable=False)
    number_of_samples = sa.Column(sa.Integer, nullable=False, default=0)
    thermomixer_time_s = sa.Column(sa.Integer, nullable=False, default=60)
    liquid_nitrogen_time_s = sa.Column(sa.Integer, nullable=False, default=60)
    number_of_cycles = sa.Column(sa.Integer, nullable=False, default=20)
    additional_notes = sa.Column(sa.String, nullable=True)
    update_time = sa.Column(sa.DateTime, default=datetime.utcnow)
    robot_logs = so.relationship('RobotLog', order_by='RobotLog.id', back_populates='experiment_setting', foreign_keys='RobotLog.experiment_id')

class RobotLog(db.Model):
    __tablename__ = 'robot_logs'
    
    id = sa.Column(sa.Integer, primary_key=True)
    experiment_id = sa.Column(sa.Integer, sa.ForeignKey('experiment_settings.experiment_id'), nullable=False)
    experiment_name = sa.Column(sa.String, sa.ForeignKey('experiment_settings.experiment_name'), nullable=True)
    action_start = sa.Column(sa.String, nullable=True)
    cycle_number = sa.Column(sa.Integer, nullable=True)
    gripper_status = sa.Column(sa.String, nullable=True)
    time_stamp = sa.Column(sa.DateTime, default=datetime.utcnow)
    error = sa.Column(sa.String, nullable=True)

    experiment_setting = so.relationship('ExperimentSetting', back_populates='robot_logs', foreign_keys=[experiment_id])