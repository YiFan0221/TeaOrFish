#計時器 可指定頻率執行 或者特定時間執行(排程)
#可以參考 https://ithelp.ithome.com.tw/articles/10218874

#year	        整數或字串	4-digit year
#month	        整數或字串	month (1-12)
#day	        整數或字串	day of the (1-31)
#week	        整數或字串	ISO week (1-53)
#day_of_week	整數或字串	number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
#hour	        整數或字串	hour (0-23)
#minute	        整數或字串	minute (0-59)
#second	        整數或字串	second (0-59)
#start_date	    整數或字串	earliest possible date/time to trigger on (inclusive)
#end_date	    整數或字串	latest possible date/time to trigger on (inclusive)

from apscheduler.schedulers.blocking import BlockingScheduler
import datetime
import requests
rs = requests.session()

sched = BlockingScheduler()

#@sched.scheduled_job('interval', minutes=25)
#def timed_job():
#    print('定期呼叫.')


@sched.scheduled_job('cron', day_of_week='mon-fri', minute='*/2')
def scheduled_job():
    print('========== APScheduler CRON =========')
    # 馬上讓我們瞧瞧
    print('This job runs every day */2 min.')
    # 利用datetime查詢時間
    st = datetime.datetime.now().ctime()
    print(st)
    
    url = "https://teaorfish.herokuapp.com"
    conn = rs.get(url)        
    
    print('========== APScheduler CRON =========')

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=17)
def scheduled_job():
    print('每周五下午5點執行--只記錄什麼都不做')

sched.start()