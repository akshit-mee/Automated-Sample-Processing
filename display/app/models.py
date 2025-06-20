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
    waiting_time_s = sa.Column(sa.Integer, nullable=False, default=5)
    number_of_cycles = sa.Column(sa.Integer, nullable=False, default=20)
    additional_notes = sa.Column(sa.String, nullable=True)
    update_time = sa.Column(sa.DateTime, default=datetime.now)

    robot_logs = so.relationship('RobotLog', order_by='RobotLog.id', back_populates='experiment_setting', foreign_keys='RobotLog.experiment_id')
    experiment_completed = so.relationship('ExperimentCompleted', back_populates='experiment_setting', foreign_keys='ExperimentCompleted.experiment_id')
    current_active = so.relationship('CurrentActive', back_populates='experiment_setting', foreign_keys='CurrentActive.experiment_id')

    def to_dict(self):
        return {
            'experiment_id': self.experiment_id,
            'experiment_name': self.experiment_name,
            'person_responsible': self.person_responsible,
            'experiment_description': self.experiment_description,
            'number_of_samples': self.number_of_samples,
            'thermomixer_time_s': self.thermomixer_time_s,
            'liquid_nitrogen_time_s': self.liquid_nitrogen_time_s,
            'waiting_time_s': self.waiting_time_s,
            'number_of_cycles': self.number_of_cycles,
            'additional_notes': self.additional_notes,
            'update_time': self.update_time.isoformat() if self.update_time else None
        }

class RobotLog(db.Model):
    __tablename__ = 'robot_logs'
    
    id = sa.Column(sa.Integer, primary_key=True)
    experiment_id = sa.Column(sa.Integer, sa.ForeignKey('experiment_settings.experiment_id'), nullable=False)
    # experiment_name = sa.Column(sa.String, sa.ForeignKey('experiment_settings.experiment_name'), nullable=True)
    action_start = sa.Column(sa.String, nullable=True)
    cycle_number = sa.Column(sa.Integer, nullable=True)
    gripper_status = sa.Column(sa.String, nullable=True)
    time_stamp = sa.Column(sa.DateTime, default=datetime.now)
    error = sa.Column(sa.String, nullable=True)

    experiment_setting = so.relationship('ExperimentSetting', back_populates='robot_logs', foreign_keys=[experiment_id])
    current_active = so.relationship('CurrentActive', back_populates='robot_log', foreign_keys='CurrentActive.robotlog_id')
    experiment_completed = so.relationship('ExperimentCompleted', back_populates='robot_log', foreign_keys='ExperimentCompleted.Robot_log_start_id')

    def to_dict(self):
        return {
            'id': self.id,
            'experiment_id': self.experiment_id,
            'experiment_name': self.experiment_setting.experiment_name, # Add reference from experiment_settings
            'action_start': self.action_start,
            'cycle_number': self.cycle_number,
            'gripper_status': self.gripper_status,
            'time_stamp': self.time_stamp.isoformat() if self.time_stamp else None,
            'error': self.error
        }
# # To add the following table for sumarising

class ExperimentCompleted (db.Model):
    __tablename__ = 'experiment_completed'
    
    id = sa.Column(sa.Integer, primary_key=True)
    experiment_id = sa.Column(sa.Integer, sa.ForeignKey('experiment_settings.experiment_id'), nullable=False)
    # experiment_name = sa.Column(sa.String, sa.ForeignKey('experiment_settings.experiment_name'), nullable=True)
    # start_time = sa.Column(sa.DateTime, nullable=False)
    # end_time = sa.Column(sa.DateTime, nullable=False)
    Robot_log_start_id = sa.Column(sa.Integer, sa.ForeignKey('robot_logs.id'), default=None)
    Robot_log_end_id = sa.Column(sa.Integer, sa.ForeignKey('robot_logs.id'), default=None)
    post_experiment_notes = sa.Column(sa.String, nullable=True)

    experiment_setting = so.relationship('ExperimentSetting', back_populates='experiment_completed', foreign_keys=[experiment_id])
    robot_log = so.relationship('RobotLog', back_populates='experiment_completed', foreign_keys=[Robot_log_start_id])
    currently_active = so.relationship('CurrentActive', back_populates='experiment_completed', foreign_keys='CurrentActive.experimet_completed_id')
    
    def to_dict(self):
        return {
            'id': self.id,
            'experiment_id': self.experiment_id,
            'experiment_name': self.experiment_setting.experiment_name, # Add reference from experiment_settings
            'start_time': self.robot_log.time_stamp.isoformat() if self.robot_log else None,
            'end_time': self.robot_log.time_stamp.isoformat() if self.robot_log else None,
            'Robot_log_start_id': self.Robot_log_start_id,
            'Robot_log_end_id': self.Robot_log_end_id,
            'post_experiment_notes': self.post_experiment_notes
        }

class CurrentActive(db.Model):
    __tablename__ = 'current_active'

    id = sa.Column(sa.Integer, primary_key=True)
    experiment_id = sa.Column(sa.Integer, sa.ForeignKey('experiment_settings.experiment_id'), nullable=False)
    # experiment_name = sa.Column(sa.String, sa.ForeignKey('experiment_settings.experiment_name'), nullable=True)
    robotlog_id = sa.Column(sa.Integer, sa.ForeignKey('robot_logs.id'), nullable=False)
    cycle_number = sa.Column(sa.Integer, nullable=False)
    experimet_completed_id = sa.Column(sa.Integer, sa.ForeignKey('experiment_completed.id'), nullable=True)

    experiment_setting = so.relationship('ExperimentSetting', back_populates='current_active', foreign_keys=[experiment_id])
    robot_log = so.relationship('RobotLog', back_populates='current_active', foreign_keys=[robotlog_id])
    experiment_completed = so.relationship('ExperimentCompleted', back_populates='currently_active', foreign_keys=[experimet_completed_id])
