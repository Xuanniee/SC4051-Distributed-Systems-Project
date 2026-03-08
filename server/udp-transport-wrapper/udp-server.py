"""
Implements the main UDP server loop.

This file should approximately contain:
	•	socket bind
	•	receive datagrams
	•	decode packet header/payload
	•	call dispatcher
	•	send reply packets
	•	print request and reply logs
	•	optional hook points for packet loss simulation

Purpose:
	•	central runtime loop of the backend server
"""