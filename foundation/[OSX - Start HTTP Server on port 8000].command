clear

#Change to current directory
cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd

# Start SimpleHTTPServer
python -m SimpleHTTPServer &> /dev/null &

clear
echo "Opening default browser"
open http://localhost:8000/
echo ""

read -p "Press [ENTER] to STOP the HTTP server on port 8000 "
#Actually kill the server
kill `ps aux | grep "python -m SimpleHTTPServer"` | grep -v grep | awk '{print $2}' > /dev/null 

echo ""
echo "Server process killed."

#Close the terminal window
#osascript -e 'tell application "Terminal" to quit'