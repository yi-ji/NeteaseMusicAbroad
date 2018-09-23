function print_log()
{
	echo "" >> helper.log
	echo $1 >> helper.log
}

function get_network_service_name()
{
	services=$(networksetup -listnetworkserviceorder | grep 'Hardware Port')

	while read line; do
	    sname=$(echo $line | awk -F  "(, )|(: )|[)]" '{print $2}')
	    sdev=$(echo $line | awk -F  "(, )|(: )|[)]" '{print $4}')
	    #echo "Current service: $sname, $sdev, $currentservice"
	    if [ -n "$sdev" ]; then
	        ifout="$(ifconfig $sdev 2>/dev/null)"
	        echo "$ifout" | grep 'status: active' > /dev/null 2>&1
	        rc="$?"
	        if [ "$rc" -eq 0 ]; then
	            currentservice="$sname"
	        fi
	    fi
	done <<< "$(echo "$services")"

	if [ -n "$currentservice" ]; then
	    echo $currentservice
	else
	    print_log "No network service, quitting"
	    exit 1
	fi
}

network_service_name=`get_network_service_name`

print_log "The change been made can be recovered at: System Preference -> Network -> Advanced -> Proxies -> Automatic Proxy Configuration."

if [ ! `networksetup -getautoproxyurl $network_service_name | grep NeteaseMusic | wc -l | xargs` = "1" ] || [ ! `networksetup -getautoproxyurl $network_service_name | grep Yes | wc -l | xargs` = "1" ] 
then
	print_log "Password is needed only for the first time."
	networksetup -setautoproxyurl $network_service_name file://`pwd`/NeteaseMusic.pac
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