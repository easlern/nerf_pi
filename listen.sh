cd /home/pi/nerf

if [ ! -f stopListening.flag ]
	then
		if [ "`ps -ef | grep listen.py | grep -v grep`" == "" ]
			then
				sudo python -u listen.py | sudo python -u updateWebListener.py
		fi
fi
