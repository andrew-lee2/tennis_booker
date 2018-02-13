from apscheduler.schedulers.blocking import BlockingScheduler

# TODO what time does heroku use?
def job_function():
    print "Hello World"

sched = BlockingScheduler()

# Schedules job_function to be run on the third Friday
# of June, July, August, November and December at 00:00, 01:00, 02:00 and 03:00
sched.add_job(job_function, 'cron', month='2', day='12', hour='15', minute=30)

sched.start()