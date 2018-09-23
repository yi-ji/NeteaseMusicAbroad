function print_log()
{
	echo "" >> helper.log
	echo $1 >> helper.log
}

print_log "The change been made can be recovered by bash: gsettings set org.gnome.system.proxy mode none"

gsettings set org.gnome.system.proxy mode auto
gsettings set org.gnome.system.proxy autoconfig-url "file://`pwd`/NeteaseMusic.pac"

nohup python NeteaseMusicProxy.py > /dev/null &

print_log "All set, you can launch your NeteaseMusic App and close me now."
print_log "Don't worry about me, I will terminate myself a few seconds after you quit NeteaseMusic."

pid=`ps x | grep NeteaseMusicProxy | awk '{print $1;}' | head -1`

while true 
do
	sleep 60
	if [ `ps x | grep netease-cloud-music | wc -l | xargs` -eq 1 ] 
	then
		kill -9 $pid
		break
	fi
done