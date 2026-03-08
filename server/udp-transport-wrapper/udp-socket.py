"""
Provides a small wrapper around Python’s UDP socket.

This file should approximately contain:
	•	sendto() wrapper
	•	recvfrom() wrapper
	•	timeout setup
	•	optional packet loss simulation hooks
	•	helper methods to keep raw socket usage cleaner

Purpose:
	•	isolate low-level socket details
"""