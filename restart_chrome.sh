#!/bin/bash

# Infinite loop to keep restarting Chrome every 10 minutes
while true; do
    # Launch Google Chrome with specific proxy settings and no sandbox mode
    google-chrome --proxy-server="http://localhost:8080" --no-sandbox &

    # Save the PID of Chrome
    CHROME_PID=$!

    # Sleep for 600 seconds (10 minutes)
    sleep 600

    # Kill the Chrome process before restarting
    kill $CHROME_PID

    # Wait a moment to ensure Chrome has fully exited
    sleep 5
done
