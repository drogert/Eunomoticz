# Eunomoticz
Python Plugin for EunO QT wallet
-
Please note that this is an very very very early alpha and still being worked on:
-
This plugin will call the wallet RPC every 30sec and update the following:
current wallet balance, current block height, current masternode count

The Masternode button will stop and start all your masternodes that are configured inside the wallet.
It will not work if you do not fill in your wallet password inside your credentials.

Add this to your euno.conf and fill in accordingly to make a connection with the wallet:
rpcallowip=
rpcusername=
rpcpassword=

Follow this guide for adding paramaters into the euno.conf
https://medium.com/@bankymoon/euno-coin-masternode-tutorial-e8326695a471


Add the files to the domoticz python plugin folder
fill in your credentials while adding hardware.

