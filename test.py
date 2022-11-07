from datetime import datetime, time

def time_in_range(start, end, current=datetime.now().time()):
    return start <= current <= end

print(time_in_range(time(1, 0, 0), time(8, 0, 0)))
print(time_in_range(time(1, 0, 0), time(8, 0, 0), time(23, 0, 0)))
print(time_in_range(time(1, 0, 0), time(8, 0, 0), time(1, 30, 0)))
print(time_in_range(time(1, 0, 0), time(8, 0, 0), time(11, 0, 0)))
