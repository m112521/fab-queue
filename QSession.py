from datetime import datetime
import json

class QueueSession:
    def __init__(self, filename, username, duration, machine):
        self.filename = filename
        self.dt_start = str(datetime.now())
        self.username = username
        self.duration = duration
        self.machine_id  = machine

    def __str__(self):
        return f"QSession: {self.filename} | {self.dt_start} | {self.username} | {self.duration} | {self.machine}"
    

if __name__=="__main__":
    qs = QSession("test.gcode", "Andrew", 120, 0)
    print(json.dumps(qs.__dict__))