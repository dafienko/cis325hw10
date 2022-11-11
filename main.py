import sys
from tkinter import *
import numpy as np
import random
import TKinterModernThemes as TKMT

from graphUtil import *

DT_MS = 10
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 600
BG_COL = "#1c1c1c"

TTKF = TKMT.ThemedTKinterFrame("HW 10", "sun-valley", "dark", usecommandlineargs=True, useconfigfile=True)
root = TTKF.root
root.title("HW 10")
root.geometry('%dx%d+%d+%d' % (SCREEN_WIDTH, SCREEN_HEIGHT+50, 1440 - (SCREEN_WIDTH+50), 50))

from Node import * # must wait to import node until after root has been created so fonts can be created

staticVar = BooleanVar()
def toggleStatic(_var, _indx, _mode):
	for n in origNodes + transClosure:
		n.static = not n.static
	
staticVar.trace_add("write", toggleStatic)
tsButton = TTKF.ToggleButton("Toggle Static Nodes", staticVar, row=2, col=2, colspan=1)

origNodes = []
transClosure = []
nodes = []

nodesVar = BooleanVar()
def toggleNodes(_var, _indx, _mode):
	global nodes

	for n in nodes:
		n.setVisible(False)

	oldNodes = nodes

	if nodes == origNodes:
		nodes = transClosure
	else:
		nodes = origNodes

	for i in range(len(nodes)):
		nodes[i].pos = oldNodes[i].pos

	for n in nodes:
		n.setVisible(True)
	
nodesVar.trace_add("write", toggleNodes)
tnButton = TTKF.ToggleButton("Toggle Transitive Closure", nodesVar, row=2, col=3, colspan=1)

canvas = Canvas(root, bg=BG_COL, height=SCREEN_HEIGHT, width=SCREEN_WIDTH)
canvas.grid(row=1, columnspan=6)

offset, scale = None, None

draggingCurrent = None
def onDragStart(event):
	global draggingCurrent, mousePos
	mousePos = np.array([float(event.x), float(event.y)])
	draggingCurrent = findClosestNode(nodes, np.array([float(event.x), float(event.y)]))
	if draggingCurrent:
		draggingCurrent.dragging = True

def onDragStop(_):
	global draggingCurrent
	if draggingCurrent:
		draggingCurrent.dragging = False
		draggingCurrent = None

SCREEN_CENTER = np.array([SCREEN_WIDTH / 2.0, SCREEN_HEIGHT / 2.0])
mousePos = SCREEN_CENTER
def onDrag(event):
	global mousePos
	mousePos = np.array([float(event.x), float(event.y)])

	if not draggingCurrent: 
		return
	
	dragNode(
		draggingCurrent, 
		mousePos, 
		offset, 
		scale, 
		SCREEN_CENTER)

canvas.bind("<ButtonPress-1>", onDragStart)
canvas.bind("<ButtonRelease-1>", onDragStop)
canvas.bind("<B1-Motion>", onDrag)

if len(sys.argv) < 2 or sys.argv[1] == "1":
	positions = [
		(.5, .1),
		(.9, .38),
		(.68, .9),
		(.32, .9),
		(.1, .38),
	]
	adjacencies = [
		[None, None, None, None, None],
		[1, None, None, None, 1],
		[None, 1, 1, None, None],
		[1, None, 1, None, 1],
		[None, None, None, 1, None],
	]
else:
	positions = [
		(.1, .38),
		(.5, .1),
		(.9, .38),
		(.68, .9),
		(.32, .9),
	]
	adjacencies = [
		[None, None, None, 30, 5],
		[15, None, None, None, None],
		[None, 5, None, 15, None],
		[None, None, 5, None, None],
		[None, None, 5, 50, None],
	]

transClosureAdjacencies = FloydWarshall(adjacencies)
for row in transClosureAdjacencies:
	for j in range(len(row)):
		row[j] = None if row[j] == None else 1

def generateNodesFromAdjacencies(adjacencies):
	nodes = []
	for i in range(len(adjacencies)):
		pos = np.array([random.randrange(SCREEN_HEIGHT - 100) + 50.0, random.randrange(SCREEN_HEIGHT - 100) + 50.0])
		n = Node(pos, canvas, nodes)

	# connect nodes according to adjacencies
	for i in range(len(adjacencies)):
		n = nodes[i]
		for ia in range(len(adjacencies[i])):
			w = adjacencies[i][ia]
			if w == None:
				continue
			n.adjacentTo(nodes[ia], w, w>1)
	return nodes

origNodes = generateNodesFromAdjacencies(adjacencies)
transClosure = generateNodesFromAdjacencies(transClosureAdjacencies)
for n in transClosure:
	n.setVisible(False)
nodes = origNodes

for i in range(len(positions)):
	nodes[i].pos = np.array([positions[i][0] * SCREEN_WIDTH, positions[i][1] * SCREEN_HEIGHT])

toggleStatic(None, None, None)

def simulate():
	global offset, scale
	for _ in range(10):
		updateNodes(nodes)
	
	res = renderNodes(nodes, SCREEN_WIDTH, SCREEN_HEIGHT)
	offset = res[0]
	scale = res[1]

	canvas.after(DT_MS, simulate)

	if draggingCurrent:
		dragNode(
			draggingCurrent, 
			mousePos, 
			offset, 
			scale, 
			SCREEN_CENTER)

simulate()
root.mainloop()