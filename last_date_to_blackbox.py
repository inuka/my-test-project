import os
import sqlite3
from datetime import date
from datetime import timedelta
from datetime import datetime

#Schedule this script after the engine generating the file that is being checked, is finished.

##### START CONFIGURATION -- EDIT THIS! -- #####

#BlackBox Location (location of blackbox.sqlite3 in the Portal python folder)
blackboxpath = os.path.join('E:\\','PORTAL','frontend','python','blackbox.sqlite3')
#Path to the generated anatella file, excluding the actual filename (to be configured below)
datapath = os.path.join('E:\\','Data','GEL\\')
#Indicate place of date in filename by <date>. Should be a file which reliably indicates the date of the tool in its filename (such as City perf for geomanager)
modules = {	"Engine":'CORE\\FCT_ER_CITY_PERF_D\\FCT_ER_CITY_PERF_D_<date>.gel_anatella',"MFS"	:'CORE\\FCT_MFS_SITE_PERF_D\\FCT_MFS_SITE_PERF_D_<date>.gel_anatella',"NTW"	:'CORE\\FCT_NTW_CELL_PERF_2G_D\\FCT_NTW_CELL_PERF_2G_D_<date>.gel_anatella'	}
#What is the right date offset for this opco? (Day minus x)
minus = 2
#Module name (GeoManager, GeoManager-MFS, Campaign Engine, ...)
product = 'GeoManager'

##### END CONFIGURATION -- EDIT THIS! -- #####


def checkLastFile(datapath,filename,module,minus):
	#get the right datestring
	day_minus = date.today() - timedelta(days=minus)
	day_minus_str = day_minus.strftime("%Y%m%d")

	date_filename = filename.replace("<date>",day_minus_str)

	isFound = False
	days_back = minus
	#check if day minus file is there
	if not os.path.isfile(os.path.join(datapath,date_filename)):
		print "minus file not found, entering loop"
		while not isFound and days_back < 30:
			#step one day back and check if the file exists, keep repeating until file is found. Limit to 30 days.
			days_back += 1
			day_minus = date.today() - timedelta(days=days_back)
			day_minus_str = day_minus.strftime("%Y%m%d")
			#print filename
			date_filename = filename.replace("<date>",day_minus_str)
			#print "checking for file: " + os.path.join(datapath,date_filename)
			if os.path.isfile(os.path.join(datapath,date_filename)):
				print "file found in loop " + `(days_back-minus)` + " days ago"
				isFound = True
	else:
		isFound = True

	if isFound:
		message = module+" module (D-" + `minus` + ' Opco) lags ' + `(days_back-minus)` + ' days behind (last successful run date: '+str(date.today() - timedelta(days=days_back))+")"
	else:
		message = "Could not find file specified, default 30 day lag"
	
	if days_back == minus:
		severity = 'INFO'
	else:
		severity = 'ERROR'

	days_lag = days_back-minus
		
	return message,severity,days_lag

def sendLagProbe(blackboxpath,product,module,message,severity,days_lag,datetime):
	metric_name = module+' lag'
	metric_type = 'Engine Stats'
	metric_details = "Indicates days the "+module+" module lags behind"
	metric_units = 'lag (days)'
	metric_value = days_lag
	log_id = -1

	#log to BlackBox
	blackbox_db = sqlite3.connect(blackboxpath)
	c = blackbox_db.cursor()
	c.execute("INSERT INTO login_blackboxlog (logId,datetime,module,severity,message,metric_name,metric_type,metric_details,metric_units,metric_value) VALUES (-1,?,?,?,?,?,?,?,?,?)", (datetime, product,severity,message,metric_name,metric_type,metric_details,metric_units,metric_value))
	blackbox_db.commit()
	blackbox_db.close()


if __name__=='__main__' :
	
	datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

	#Check all modules
	for module,filename in modules.iteritems():
		#Generate filename with datestring
		print "\n+*****************************+\n"+"| Checking module "+module+"\t\t\n+*****************************+"
		message,severity,days_lag = checkLastFile(datapath,filename,module,minus)
		print message
		#Report probe
		sendLagProbe(blackboxpath,product,module,message,severity,days_lag,datetime)



