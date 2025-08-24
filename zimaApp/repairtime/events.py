from sqlalchemy import event

from zimaApp.repairtime.models import RepairTime


@event.listens_for(RepairTime, 'before_insert')
@event.listens_for(RepairTime, 'before_update')
def receive_before_insert_or_update(mapper, connection, target):
    if target.start_time and target.end_time:
        delta_hours = (target.end_time - target.start_time).total_seconds() / 3600
        if delta_hours > 22:
            target.Duration_repair = 22
        else:
            target.Duration_repair = delta_hours