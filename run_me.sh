function print_log()
{
	echo "" >> helper.log
	echo $1 >> helper.log
}

print_log "The change been made can be recovered at: System Preference -> Network -> Advanced -> Proxies -> Automatic Proxy Configuration."

if [ ! `networksetup -getautoproxyurl wi-fi | grep NeteaseMusic | wc -l | xargs` = "1" ] || [ ! `networksetup -getautoproxyurl wi-fi | grep Yes | wc -l | xargs` = "1" ] 
then
	print_log "Password is needed only for the first time."
	networksetup -setautoproxyurl wi-fi file://`pwd`/NeteaseMusic.pac
fi

nohup python NeteaseMusicProxy.py > /dev/null &

print_log "All set, you can launch your NeteaseMusic App and close me now."
print_log "Don't worry about me, I will terminate myself a few seconds after you quit NeteaseMusic."

pid=`ps x | grep NeteaseMusicProxy | awk '{print $1;}' | head -1`

while true 
do
	sleep 60
	if [ `ps x | grep MacOS/NeteaseMusic | wc -l | xargs` -eq 1 ] 
	then
		kill -9 $pid
		break
	fi
done