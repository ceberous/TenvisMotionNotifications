import multiprocessing
from flask import Flask , render_template , jsonify

from tenvisController import TenvisVideo

notificationStatus = False
wPID = None

w_globalProcess = None
def launchTenvisController():
	myTV = TenvisVideo()


app = Flask( __name__ )

@app.route("/")
def displayHome():
        return render_template( 'index.html'  )


@app.route( "/state" , methods=['GET'] )
def getState():
	global notificationStatus
        if notificationStatus is False:
                return jsonify({ "state" : "off" })
        else:
                return jsonify({ "state" : "on" })      

@app.route( "/turnon" , methods=['GET'] )
def turnON():
	global notificationStatus
        notificationStatus = True
	global w_globalProcess
	w_globalProcess = multiprocessing.Process( name='wGP' , target=launchTenvisController )
	w_globalProcess.daemon = True
	w_globalProcess.start()
	return jsonify({ "result" : "turned ON notifications" })


@app.route( "/turnoff" , methods=['GET'] )
def turnOFF():
	global notificationStatus
        notificationStatus = False
	global w_globalProcess
	w_globalProcess.terminate()
	return jsonify({ "result" : "turned OFF notifications" })




app.run( '0.0.0.0' , 8080 )
