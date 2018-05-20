# Python_NetworkX

Program displays maps for Disney World.

When	the program	runs,	it	must:
o Alphabetically	list	all	the	attractions it	knows	about. Number	them	for	easy	user	data	
entry. This	list	should	be	derived	by	iterating	through	the	graph	nodes.
o Ask	the	user	to	enter	their	starting	point	and	the next attraction	they	want	to	visit.
o Ask	whether	they	require	a	handicapped-accessible	route (which	should	affect	which	
paths	are	feasible – a	creative,	dynamic	usage	of	edge	'weighting'	will	solve	this).
o Then	it	will	calculate	a shortest path and	print	clear turn-by-turn	navigation	
instructions with total	distance.
o Then	it	should	allow	the	user	to	quit	or	enter	another	navigation	query,	which	defaults	
to	starting	at	the	last	e
590PR	Spring	2018.	Assignment	7 page 3

The	shortest	path	calculations	must	be	dynamically	derived	from	the	graph,	not	predetermined.
	For	example,	if	a	construction	project	closes	a	path segment,	we	should	be	able	
to	temporarily	either	remove	that	edge	or	temporarily	change	its	“distance” to	a	very	high	
number	so	that	routes	normally	through	it	will	get	re-routed without	altering	your	program.
The	algorithm(s)	you	need	are	already	part	of	NetworkX.

Lastly,	include	an	automated	test	that	verifies	that	it	is	possible	to	navigate from	every
attraction	in	your	facility	to	every	other facility.		You	don't	want	visitors	getting	strande
