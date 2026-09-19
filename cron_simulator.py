import time
import threading
import datetime

# A simple class to represent a cron job
class CronJob:
    def __init__(self, schedule_str, command):
        self.schedule_str = schedule_str
        self.command = command
        self.last_run = None
        self.schedule = self.parse_schedule(schedule_str)

    def parse_schedule(self, schedule_str):
        # Basic parsing for minute, hour, day of month, month, day of week
        # Example: "* * * * *" means every minute
        # "0 12 * * 1" means at 12:00 on Mondays
        parts = schedule_str.split()
        if len(parts) != 5:
            raise ValueError("Invalid cron schedule string format. Expected 5 parts.")
        return {
            'minute': self.parse_part(parts[0], 0, 59),
            'hour': self.parse_part(parts[1], 0, 23),
            'day_of_month': self.parse_part(parts[2], 1, 31),
            'month': self.parse_part(parts[3], 1, 12),
            'day_of_week': self.parse_part(parts[4], 0, 6) # 0=Sunday, 6=Saturday
        }

    def parse_part(self, part, min_val, max_val):
        # Handles '*', ',', '-' and specific numbers
        values = set()
        if part == '*':
            return set(range(min_val, max_val + 1))
        
        sub_parts = part.split(',')
        for sub_part in sub_parts:
            if '-' in sub_part:
                start, end = map(int, sub_part.split('-'))
                values.update(range(start, end + 1))
            else:
                values.add(int(sub_part))
        return values

    def is_due(self, current_time):
        # Check if the current time matches the schedule
        if self.schedule['minute'] != '*' and current_time.minute not in self.schedule['minute']:
            return False
        if self.schedule['hour'] != '*' and current_time.hour not in self.schedule['hour']:
            return False
        if self.schedule['day_of_month'] != '*' and current_time.day not in self.schedule['day_of_month']:
            return False
        if self.schedule['month'] != '*' and current_time.month not in self.schedule['month']:
            return False
        # Day of week check: 0=Sunday, 6=Saturday. Python's weekday() is 0=Monday, 6=Sunday.
        # We need to adjust Python's weekday to match cron's convention.
        cron_day_of_week = (current_time.weekday() + 1) % 7 
        if self.schedule['day_of_week'] != '*' and cron_day_of_week not in self.schedule['day_of_week']:
            return False
        
        # Prevent running multiple times in the same minute if the job is very fast
        if self.last_run and self.last_run.year == current_time.year and \
           self.last_run.month == current_time.month and self.last_run.day == current_time.day and \
           self.last_run.hour == current_time.hour and self.last_run.minute == current_time.minute:
            return False

        return True

    def run(self):
        print(f"[{datetime.datetime.now()}] Running job: '{self.command}' with schedule '{self.schedule_str}'")
        # In a real scenario, you would execute the command here.
        # For simulation, we just print.
        self.last_run = datetime.datetime.now()

class CronScheduler:
    def __init__(self):
        self.jobs = []
        self._stop_event = threading.Event()

    def add_job(self, schedule_str, command):
        try:
            job = CronJob(schedule_str, command)
            self.jobs.append(job)
            print(f"Added job: '{command}' with schedule '{schedule_str}'")
        except ValueError as e:
            print(f"Error adding job: {e}")

    def run_scheduler(self):
        print("Cron scheduler started. Press Ctrl+C to stop.")
        while not self._stop_event.is_set():
            now = datetime.datetime.now()
            for job in self.jobs:
                if job.is_due(now):
                    # Run in a separate thread to avoid blocking the scheduler loop
                    thread = threading.Thread(target=job.run)
                    thread.start()
            
            # Sleep for a short interval (e.g., 10 seconds) to check periodically
            time.sleep(10)

    def stop_scheduler(self):
        self._stop_event.set()
        print("Cron scheduler stopping...")

def main():
    scheduler = CronScheduler()

    # Example Cron Jobs:
    # 1. Run a command every minute
    scheduler.add_job("* * * * *", "echo 'This runs every minute'")
    
    # 2. Run a command at 10:30 AM every day
    scheduler.add_job("30 10 * * *", "echo 'This runs daily at 10:30 AM'")
    
    # 3. Run a command at 5:00 PM on Fridays
    # Cron day of week: 0=Sun, 1=Mon, ..., 5=Fri, 6=Sat
    scheduler.add_job("0 17 * * 5", "echo 'This runs every Friday at 5:00 PM'")
    
    # 4. Run a command on the 1st of every month at midnight
    scheduler.add_job("0 0 1 * *", "echo 'This runs on the 1st of every month'" )

    # 5. Run a command every 15 minutes
    scheduler.add_job("*/15 * * * *", "echo 'This runs every 15 minutes'")

    # 6. Run a command on weekdays at 9 AM
    scheduler.add_job("0 9 * * 1-5", "echo 'This runs on weekdays at 9 AM'" )

    try:
        scheduler.run_scheduler()
    except KeyboardInterrupt:
        scheduler.stop_scheduler()

if __name__ == "__main__":
    main()
