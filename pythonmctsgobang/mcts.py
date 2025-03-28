import time
import math
import random
from pythonmctsgobang.point import Point
from pythonmctsgobang.publictool import posIsValid, checkWin
from pythonmctsgobang.globals import *
from typing import Self
class Node:

	def __init__(self, theState, theParent, theNowColor):
		# 这里可能还要初始化一下其他成员
		self.state = theState
		self.parent = theParent
		self.nowColor = theNowColor
		self.visits = 0
		self.wins = 0
		self.children = []

	def getPossibleMoves(self) -> set:
        # 获取当前状态下所有可能的动作
		dx = [0, 1, 1, 1]
		dy = [1, 1, 0, -1]
		s = set()
		def func1(p, sign, i):
			nonlocal s
			tx = p.x+sign*dx[i]
			ty = p.y+sign*dy[i]
			if not posIsValid(tx, ty,self.state):
				return
			if (tx, ty) not in s:
				s.add((tx, ty))
		for p in self.state:
			for i in range(4):
				sign = 1
				func1(p, sign, i)
				sign = -1
				func1(p, sign, i)
		return s

	def expandNodes(self):
		s = self.getPossibleMoves()  # 获取当前状态下所有可能的动作
		if len(self.children) == 0:  # 当前节点完全没有子节点
			for n in s:
				newState = self.state.copy()
				newState.append(Point(self.nowColor, n[0], n[1]))
				newNode = Node(newState, self, -self.nowColor)
				self.children.append(newNode)

	def calculateUCB(self):
		if self.parent is None:
			raise Exception("calculate UCB for node with no parent")
		# 这里在计算的时候要处理一下除0异常
		ucb = math.inf
		if self.parent.visits == 0 or self.visits == 0:
			return ucb
		rate = self.wins/self.visits # 算的是从父状态到当前状态所落子后黑子的胜率
		# 这里还要区分一下下一步落子的颜色，计算胜率的时候会有所不同，因为wins代表的是黑色节点胜利的次数，对于白色节点来说要用1-黑色节点胜率
		# 如果当前状态下该落白子了，说明导致该局面的是一枚黑子的落下，所以当self.nowColor为-1时，胜率应该是rate，否则应该是1-rate
		winRate = rate if self.nowColor == -1 else 1-rate
		ucb = winRate + UCB_WEIGHTS * math.sqrt(math.log(self.parent.visits) / self.visits)
		return ucb
	
	def getBestChild(self)->None|Self:
		# 选择胜率最大的孩子节点，如果有多个，随机选择一个
		bestChildren=[]
		bestRate=-1
		for child in self.children:
			try:
				rate=1-child.wins/child.visits # 由于AI拿的是白棋，wins记录的是人类黑棋的胜利次数，所以这里要用1-wins/visits
			except ZeroDivisionError:
				rate=-math.inf
			if rate>bestRate:
				bestChildren.clear()
				bestRate=rate
				bestChildren.append(child)
			elif rate==bestRate:
				bestChildren.append(child)
		if len(bestChildren)==0:
			return None
		bestChild=bestChildren[random.randint(0,len(bestChildren)-1)]
		return bestChild
class MCTS:

	def __selection(self,node: Node):
		hasIter=False
		while len(node.children) != 0: 
			ucbs=[]
			largestUCB=-1
			for child in node.children:
				ucbValue=child.calculateUCB()
				if ucbValue>largestUCB:
					ucbs.clear()
					largestUCB=ucbValue
					ucbs.append(child)
			index=random.randint(0,len(ucbs)-1)
			node=ucbs[index]
			hasIter=True
		return node,hasIter
			
	def __expand(self,node:Node):
		node.expandNodes(); # 获取当前状态下所有可能的动作，然后将这些动作作为子节点加入当前节点node的children中

	def __rollout(self,node:Node):
		# 不停的随机下棋，直到游戏结束
		while not checkWin(node):
			possibleMoves=node.getPossibleMoves()
			randMove=random.choice(tuple(possibleMoves))
			newState=node.state.copy()
			newState.append(Point(node.nowColor,randMove[0],randMove[1]))
			node=Node(newState,node,-node.nowColor)
		return node
	def __backPropagation(self,endNode:Node,node:Node):
		# 将endNode的价值，也就是胜率计算出来，然后沿着node一路向上反向传播更新节点的关键值
		# 先判断一下最后到底是输了还是赢了，所有相关信息都存储到了endNode中，只要看一下endNode保存的棋步数组的最后一个点是什么颜色就行
		resColor=endNode.state[-1].color
		# 一直向上回溯直到根节点
		# TODO 只更新了从当前节点一直到“父节点不为空”为止，这可能导致根节点没有更新
		while node != None:
			# 只有在黑棋最终获胜的情况下（resColor==1）才会给胜利次数+1，wins代表的是黑色节点胜利的次数
			node.wins += 1 if resColor==1 else 0
			node.visits += 1
			node=node.parent
			
	# MCTS迭代循环的主函数
	def iteration(self,state:list,nowcolor:int,newRoot:Node|None)->tuple[Point,Node]|None:
		"""
		state: 当前的棋盘状态，是一个Point的列表，每个Point代表一个棋子的位置
		nowcolor: 当前应该落子的颜色
		"""
		# startTime=time.perf_counter()
		iterNum=0
		if newRoot is not None:
			root=newRoot
		else:
			root=Node(state,None,nowcolor)
		node=root # node这个引用所指向的节点在后面会不断的变化，但是root节点是不会变的，最后要从root节点的孩子节点中挑一个最好的
		while iterNum < MAX_ITER_NUM:
			# curTime=time.perf_counter()
			# if curTime-startTime>=MAX_ITER_TIME:
			# 	break
			node,hasIter=self.__selection(node)
			# select之后按照情况决定是expand还是rollout
			if hasIter and node.visits == 0:
				# 如果上一步经过迭代选择，且当前节点没有被探索过，那么就该rollout了
				endNode=self.__rollout(node) #endNode是一个已经胜利的node
				self.__backPropagation(endNode,node)
			else:
				# 如果上一步没有经过迭代选择，那说明需要扩展节点
				self.__expand(node)
			iterNum+=1
			node=root
		# 选择最好的节点
		bestChild=root.getBestChild()
		if bestChild is None:
			return None
		# TODO 也许可以把bestChild也返回，下一次迭代可以直接从这个节点开始
		return bestChild.state[-1],bestChild