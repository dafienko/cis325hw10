from math import ceil
import re

# length of the string that is *D*isplayed (remove invisible escape sequences, then take len)
def dlen(s):
	return len(re.sub("\033\[([0-9,]*;?)*m", "", s))

def cjust(s, w):
	extra = w - len(s)
	return " " * (extra // 2) + s + " " * ceil(extra / 2)

def combineTextRectangles(lineRectangles, separator):
	combined = []
	height = 0
	for r in lineRectangles:
		height = max(height, len(r))
	
	for i in range(height):
		lines = []
		for rect in lineRectangles:
			if i >= len(rect):
				lines += [" " * dlen(rect[0])]
			else:
				lines += [rect[i]]
		
		combined.append(separator.join(lines))
	return combined


def centerTextRect(textRect, w):
	for i in range(len(textRect)):
		textRect[i] = cjust(textRect[i], w)
	return textRect

"""
┏    ┓
┃    ┃
┗    ┛
"""

N_PADDING = 1
N_WIDTH = 3
HIGHLIGHT_STR = "\033[97;46m"
RESET_STR = "\033[0m"
def FWMatStr(mat, k):
	n = len(mat) 
	res = " " * (N_WIDTH*n + N_PADDING*(n+1))
	bottomLine = "┗" + res + "┛"
	res = "┏" + res + "┓\n"

	for i in range(n):
		row = mat[i]
		res += "┃" + " " * N_PADDING
		if i == k:
			res += HIGHLIGHT_STR

		for j in range(n):
			w = row[j]
			if i != k and j == k:
				res += HIGHLIGHT_STR
			
			res += cjust("∞" if w == None else str(w), N_WIDTH) + " " * N_PADDING

			if i != k and j == k:
				res += RESET_STR

		if i == k:
			res += RESET_STR

		res += "┃\n"

	return res + bottomLine

def FloydWarshall(graph):
	res = []
	for r in range(len(graph)):
		res.append([])
		for c in range(len(graph)):
			res[r].append(graph[r][c])

	initStr = FWMatStr(res, None)

	stageStrings = []
	for k in range(len(graph)):
		pre = FWMatStr(res, k).split("\n")
		for r in range(len(graph)):
			for c in range(len(graph)):
				if r == k or c == k:
					continue
				
				x = res[k][c] 
				y = res[r][k]
				if x == None or y == None:
					continue

				if res[r][c] == None:
					res[r][c] = x + y
				else:
					res[r][c] = min(res[r][c], x + y)
		
		post = FWMatStr(res, None).split("\n")
		middle = ["  "] * len(graph)
		middle[len(graph) // 2 + 1] = "->"

		full = combineTextRectangles([pre, middle, post], " ")
		stageStrings.append(cjust("k = " + str(k+1), len(full[0])) + "\n" + "\n".join(full))

	initStr = initStr.split("\n")
	initStr.insert(0, cjust("init", len(initStr[0])))
	fullWidth = len(stageStrings[0].split("\n")[0]) * 2 + 4
	print("\n".join(centerTextRect(initStr, fullWidth)))

	for i in range(0,len(stageStrings), 2):
		if i + 1 < len(stageStrings):
			a = stageStrings[i].split("\n")
			b = stageStrings[i+1].split("\n")
			print("\n".join(combineTextRectangles([a, b], "    ")))
		else:
			print(stageStrings[i])
		print()

	post.insert(0, cjust("final", len(post[0])))
	print("\n".join(centerTextRect(post, fullWidth)))

	return res 