#**************************************************************
# Script to collect performance counter values for all events
#**************************************************************
#!/bin/bash


#Check number of command line arguments
if [ "$#" -lt 4 ]; then
	echo "Usage: bash ./perfToolUtilScript.sh <output-zipname> <sampling-interval-per-event-milliseconds> <sleep-duration> <initialization-time-in-seconds>";
	exit 1
fi

#Extract values from command line args
outputfolder=$1
samplingtime=$2
totalduration=$3
initializationtime=$4

#If output folder previously exists, remove
if [ -d $outputfolder ]; then
	echo "Deleting previously existing $outputfolder"
	rm -rf $outputfolder
fi

rm -rf $outputfolder.zip

#Create output folder
mkdir $outputfolder

cp configFile $outputfolder/
cd $outputfolder

for event in $(cat configFile);
do

	firefox https://www.youtube.com/watch?v=00yyCMJWIpA &
	#google-chrome-stable https://www.youtube.com/watch?v=00yyCMJWIpA --user-data-dir /home/justinekays/abc &
	#gedit test.txt &
	#soffice -nologo -show /home/justinekays/test.odp -norestore &
	#totem /home/justinekays/Downloads/video.mp4 &
	#geany /home/justinekays/FEPerfUtil.c /home/justinekays/	perfToolUtilScript.sh /home/justinekays/	perf_event_open.html &
	#supertux2 --disable-music &
	#pid=$(pgrep watchdog | head -n 1)
	##FoxitReader /home/justinekays/14GADM-Final.pdf &
	#7z a abc.zip /home/justinekays/ &
	pid=$!
	sleep $initializationtime

	#pid=$(pgrep soffice.bin)
	#Get process ID of monitored process 
	echo $pid

	mkdir $event
	cd $event

	#Read events to read from config file
	perf stat -e $event -I $samplingtime -p $pid sleep $totalduration 2> raw_counters_$event.txt

	for i in $(echo $event | tr "," "\n")
	do
		grep $i raw_counters_$event.txt > raw_counters_$i.txt 
		awk -F ' ' '{print $2}' raw_counters_$i.txt  > counter_values_$i.txt
		sed -i 's/,//g' counter_values_$i.txt
		grep '[0-9]' counter_values_$i.txt | sponge counter_values_$i.txt
		rm raw_counters_$i.txt
	done

	kill -s SIGTERM $pid
	sleep 180
	cd ..
done

rm configFile
rm -rf pid.txt

#Zip output event files
zip -r $outputfolder.zip *

#Go to the parent folder where you initially started execution
cd ..

#Copy output folder zip archive here
cp $outputfolder/$outputfolder.zip .

#Remove output folder
rm -rf $outputfolder

exit

