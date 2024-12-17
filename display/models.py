from datetime import datetime
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db

class ExperimentSetting(db.Model):
    __tablename__ = 'experiment_settings'
    
    id = sa.Column(sa.Integer, primary_key=True)
    project_id = sa.Column(sa.String, nullable=False)
    project_name = sa.Column(sa.String, nullable=False)
    person_responsible = sa.Column(sa.String, nullable=True)
    thermomixer_time_s = sa.Column(sa.Integer, nullable=False, default=60)
    liquid_nitrogen_time_s = sa.Column(sa.Integer, nullable=False, default=60)
    number_of_cycles = sa.Column(sa.Integer, nullable=False, default=20)
    update_time = sa.Column(sa.DateTime, default=datetime.timezone.utcnow)

class RobotLog(db.Model):
    __tablename__ = 'robot_logs'
    
    id = sa.Column(sa.Integer, primary_key=True)
    project_id = sa.Column(sa.String, sa.ForeignKey('experiment_settings.project_id'), nullable=False)
    project_name = sa.Column(sa.String, sa.ForeignKey('experiment_settings.project_name'), nullable=False)
    action_start = sa.Column(sa.String, nullable=True)
    cycle_number = sa.Column(sa.Integer, nullable=True)
    gripper_status = sa.Column(sa.String, nullable=True)
    time_stamp = sa.Column(sa.DateTime, default=datetime.timezone.utcnow)
    error = sa.Column(sa.String, nullable=True)

    experiment_setting = so.relationship('ExperimentSetting', back_populates='robot_logs')

ExperimentSetting.robot_logs = so.relationship('RobotLog', order_by=RobotLog.id, back_populates='experiment_setting')