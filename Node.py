import numpy as np
from tkinter import *
from tkinter import font
from math import sqrt, pow

NODE_RADIUS = 20
NODE_FONT = font.Font(family='Helvetica',size=18)
EDGE_EQUILIBRIUM = 150
EDGE_STRENGTH = .009
NODE_REPULSION = 200
BG_COL = "#1c1c1c"

def vToS(v):
	return "(%.0f, %.0f)" % (v[0], v[1])

def rPosToWorldPos(p, offset, scale, screenCenter):
	v = p - screenCenter 
	v /= scale 
	p = screenCenter + v
	p -= offset
	return p

def findClosestNode(nodes, p):
	closest, cDist = None, 0
	for n in nodes:
		d = np.linalg.norm(p - n.rPos)
		if not closest or d < cDist:
			cDist = d
			closest = n

	return closest if cDist < NODE_RADIUS else None

def dragNode(draggingNode, mPos, offset, scale, screenCenter):
	draggingNode.pos = rPosToWorldPos(mPos, offset, scale, screenCenter)

class Node:
	def __init__(self, pos, canvas, nodes):
		self.canvas = canvas
		self.val = len(nodes) + 1 
		self.pos = pos
		self.rPos = pos
		self.ellipse = canvas.create_oval(0, 0, NODE_RADIUS*2, NODE_RADIUS*2, fill=BG_COL, outline="white", width=3)
		self.text = canvas.create_text(0, 0, text=str(self.val), fill="white", font=NODE_FONT)
		self.edges = []
		self.edgeLabels = []
		self.adjacentNodes = []
		self.netForce = np.array([0.0, 0.0])
		self.static = False
		self.dragging = False
		
		nodes.append(self)

		self.render()

	def setVisible(self, visible):
		state = "normal" if visible else "hidden"
		for o in [self.ellipse, self.text] + self.edges + self.edgeLabels:
			self.canvas.itemconfigure(o, state=state)

	def computeForce(self, nodes):
		# node repulsion force
		for on in nodes:
			if on.val <= self.val:
				continue 

			v = on.pos - self.pos
			m = np.linalg.norm(v)
			if m > 2*EDGE_EQUILIBRIUM:
				continue

			u = v / m
			f = (NODE_REPULSION / (m**1.6)) * u

			self.netForce -= f 
			on.netForce += f

		# edge spring force
		for an in self.adjacentNodes:
			v = an.pos - self.pos
			m = np.linalg.norm(v)
			if m <= 0: 
				continue
			u = v / m
			dx = m - EDGE_EQUILIBRIUM
			f = u * dx * EDGE_STRENGTH
			
			self.netForce += f 
			an.netForce -= f

	def setColor(self, fill=BG_COL, accent="white"):
		self.canvas.itemconfig(self.ellipse, fill=fill, outline=accent)
		self.canvas.itemconfig(self.text, fill=accent)
		for e in self.edges:
			self.canvas.itemconfig(e, fill=accent)

	def update(self):
		if not (self.static or self.dragging):
			self.pos += self.netForce
		
	def adjacentTo(self, node, weight, showWeight):
		self.adjacentNodes.append(node)

		e = self.canvas.create_line(self.pos[0], self.pos[1], node.pos[0], node.pos[1], arrow=LAST, fill="white", width=2, arrowshape=(10,12,6), smooth=True)
		t = None 
		if showWeight:
			t = self.canvas.create_text(0, 0, text=str(weight), fill="white", font=NODE_FONT)
			self.canvas.tag_lower(t)
		
		self.canvas.tag_lower(e)
		
		self.edges.append(e)
		self.edgeLabels.append(t)

	def updateRenderPos(self, offset, scale, W, H):
		rp = self.pos + offset
		center = np.array([W/2.0, H/2.0])
		v = rp - center
		v *= scale
		rp = center + v
		self.rPos = (round(rp[0]), round(rp[1]))

	def render(self):
		# render self
		self.canvas.moveto(self.ellipse, self.rPos[0] - NODE_RADIUS, self.rPos[1] - NODE_RADIUS)
		textBounds = self.canvas.bbox(self.text)
		tw = textBounds[2] - textBounds[0]
		th = textBounds[3] - textBounds[1]
		self.canvas.moveto(self.text, self.rPos[0] - tw//2, self.rPos[1] - th//2)

		# render edges
		for i in range(len(self.adjacentNodes)):
			edge = self.edges[i]
			label = self.edgeLabels[i]
			adjacentNode = self.adjacentNodes[i]
			vx, vy = adjacentNode.rPos[0] - self.rPos[0], adjacentNode.rPos[1] - self.rPos[1]
			arrowSpace = NODE_RADIUS + 2
			m = sqrt(pow(vx, 2) + pow(vy, 2))
			if m <= 0:
				continue

			ux, uy = (vx/m) * arrowSpace, (vy/m) * arrowSpace
			
			nx, ny = -vy, vx
			mOff = .1
			mx, my = self.rPos[0] + vx/2 + nx*mOff, self.rPos[1] + vy/2 + ny*mOff

			self.canvas.coords(
				edge, self.rPos[0] + ux, self.rPos[1] + uy,  
				mx, my,
				adjacentNode.rPos[0] - ux*1.5, adjacentNode.rPos[1] - uy*1.5)
			if label:
				self.canvas.moveto(label, mx - nx*mOff*.5, my - ny*mOff*.5)


def updateNodes(nodes):
	for n in nodes:
		n.netForce = np.array([0.0, 0.0])

	for n in nodes: 
		n.computeForce(nodes)
	
	for n in nodes:
		n.update()

currentScale = 0
currentOffset = np.array([0.0, 0.0])
def renderNodes(nodes, W, H):
	global currentScale, currentOffset 

	# compute offset/sclae to center graph in the middle of the screen
	tl, br = nodes[0].pos.copy(), np.array([0.0, 0.0])
	for n in nodes:
		tl[0] = min(tl[0], n.pos[0])
		tl[1] = min(tl[1], n.pos[1])
		br[0] = max(br[0], n.pos[0])
		br[1] = max(br[1], n.pos[1])
	middle = (tl + br) / 2
	borderPadding = 50.0
	boundSize = br - tl + np.array([borderPadding, borderPadding]) * 2
	scale = min(W / boundSize[0], H / boundSize[1]) 

	offset = np.array([W, H])/2 - middle

	alpha = .1
	currentScale = (1-alpha)*currentScale + alpha*scale
	currentOffset = (1-alpha)*currentOffset + alpha*offset
	for n in nodes:
		n.updateRenderPos(currentOffset, currentScale, W, H)

	for n in nodes:
		n.render()
	
	return currentOffset, currentScale