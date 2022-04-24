import tkinter as tk
from tkinter.constants import *
from random import randint as rint, random as rand, sample, choice
from time import sleep, monotonic
from numpy import ceil, zeros
from inspect import getmembers

import config
from GridClass import Grid


class wBob:


	def __init__(self):	

		self.root = tk.Tk()

		LARG, HAUT = 600, 480
		root_offX, root_offY = 100, 100
		self.root.geometry('{}x{}+{}+{}'.format(LARG, HAUT, root_offX, root_offY))
		self.root.maxsize(LARG, HAUT)
		self.root.title('Snakemare')

		self.can = tk.Canvas(self.root, width=LARG, height=HAUT, bg='black')
		self.can.pack(fill=BOTH)
		self.can.focus_set()
		config.master_ = self.can

		self.gridOffX, self.gridOffY = 150, 60 
		self.gridLARG, self.gridHAUT = LARG-self.gridOffX-30, HAUT-self.gridOffY-30
		gridCell_Dimention = (13,13)
		self.grid_nbCols , self.grid_nbLigs = int(self.gridLARG / gridCell_Dimention[0]), int(self.gridHAUT / gridCell_Dimention[1])

		print(self.grid_nbCols , self.grid_nbLigs)
		#print('grid_nbCols et grid_nbLigs :', self.grid_nbCols , self.grid_nbLigs)
		self.grid = Grid(self.gridLARG, self.gridHAUT, self.grid_nbCols, self.grid_nbLigs, offsetX= self.gridOffX, offsetY= self.gridOffY)
		config.grid_ = self.grid
		#print(self.grid)

		# Pour dessiner les blocs du corps du serpent plus petit que la cellule.
		self.gridCell_10pX = self.grid.CellLARG*0.1 
		self.gridCell_10pY = self.grid.CellHAUT*0.1

		[ self.can.create_line(*self.grid.find_coord((col, 0)), *self.grid.find_coord((col, self.grid.nbLigs_)), fill='blue', width=2, state='hidden', tags='Grid') for col in range(1, self.grid_nbCols)]
		[ self.can.create_line(*self.grid.find_coord((0, lig)), *self.grid.find_coord((self.grid.nbCols_, lig)), fill='blue', width=2, state='hidden', tags='Grid') for lig in range(1, self.grid_nbLigs)]

		self.can.create_rectangle(*self.grid.find_coord((0, 0)), *self.grid.find_coord((self.grid_nbCols, self.grid_nbLigs)), fill='', outline='light blue', width='4', tags='frame')
		self.can.create_rectangle(*self.grid.find_coord((0, 0)), *self.grid.find_coord((self.grid_nbCols, self.grid_nbLigs)), fill='black', tags='gridBG')
		self.can.tag_lower('gridBG')

		self.roundy = lambda nb, tol=2: int(nb*(10**tol)+0.5)/(10**tol)

		self.snake = [(1,1),(2,1)]
		self.snake_peauMorte = dict()
		self.snake_col = 'light green'

		self.tête = zeros(2,int)
		self.tête[0], self.tête[1] = self.snake[-1][0], self.snake[-1][1]
		self.têteOffset = zeros(2,int)
		self.têteOffset[0], self.têteOffset[1] = (0,0)
		self.pomme = zeros(2,int)
		self.pomme[0], self.pomme[1] = (rint(0,self.grid_nbCols-1), rint(0,self.grid_nbLigs-1)) # inedex de grid
		self.pommeCoord = [*self.grid.find_coord( self.pomme )]		# coord dans can

		print('Mem ID de pommeCoord',id(self.pommeCoord))
		self.direction = 'D'

		self.PowerUp_chance = 0.6
		
		#Vitesse
		#Indice de vitesse actuelle de 1-9.
		self.gear = tk.IntVar(value=1) #vitesse_actuelle = vitesse_base / gear = ms/frame 

		self.vitesse_Base = 500
		self.vitesse_actuelle = int(self.vitesse_Base / self.gear.get())

		self.speedCap = 	{'normal': 	lambda vit: vit,						# vitesse normale
							 'ram':  	lambda vit: vit if vit > 200 else 200}	# vitesse limitée 200

		self.speedMod = 	{'normal': 	lambda vit:	vit,						# vitesse normale
							 'double':	lambda vit: vit/2,						# vitesse doublée
							 'half'	 :	lambda vit: vit*2 }						# vitesse moitiée
		
		self.speedCap_actu = 'normal'
		self.speedMod_actu = 'normal'
		

		# SCORES_
		self.longueur = tk.IntVar(value=len(self.snake))

		
		#Temps
		self.temps_total = tk.IntVar(value=1)
		self.temps_dernPomme = monotonic()

		#Score
		self.score_Base = 1000
		self.score_modArray = []
		self.score_modif = tk.IntVar(value= 1) 	# multiplicateur de score
		self.score_actuelle = tk.IntVar(value=0)

		#Combo
		self.combo_delay = 3000 # sec
		self.combo_timer = 0
		self.combo_timerEvent = 0
		self.combo_modif = tk.IntVar(value=1) # multiplicateur de score, aditionné à sceore_modif
		
		self.total_scoreModif = tk.IntVar(value= 1)
		# _SCORES



		# LOAD TopScores_
		try:
			with open('Snake_TopScores.txt', 'r') as TopFile:	
				self.TopScore, self.TopTemps, self.TopLong, self.TopScoreSec, self.TopCombo = [ int(TopLig.split('=')[1].strip('\n')) for TopLig in TopFile.readlines()]

		except FileNotFoundError:

			self.TopScore = 0
			self.TopTemps = 0
			self.TopLong = 0	
			self.TopScoreSec = 0
			self.TopCombo = 0
		# _LOAD TopScores


		# Game State_
		self.GameOn = True
		self.GAMEOVER = False
		# Game State_


		# PreGame features loading_
		self.segLARG = 	self.grid.CellLARG-self.gridCell_10pX
		self.segHAUT =  self.grid.CellHAUT-self.gridCell_10pY


		self.segCoords_temp =  zeros((2,2),int)#[[0,0],[0,0]]	# espace réservé pour les coords du nouveau seg créé chaque gameLoop
		for segment in self.snake:

			self.segmentCoord(segment)
			self.can.create_rectangle(*self.segCoords_temp[0], *self.segCoords_temp[1], fill= self.snake_col, state='hidden' ,tags='Snake')

		self.can.create_oval(self.pommeCoord[0]+self.gridCell_10pX, self.pommeCoord[1]+self.gridCell_10pY, self.pommeCoord[0]+self.grid.CellLARG-self.gridCell_10pX, self.pommeCoord[1]+self.grid.CellHAUT-self.gridCell_10pY,
		fill='red', outline='black', width=3, state='hidden' ,tags='Pomme')
		# _PreGame features loading


		# GameLoop Utils_
		self.rawMove = zeros(2,int) #[0,0]
		self.filteredMove = zeros(2,int) #[0,0]

		def moveG():	self.rawMove[0], self.rawMove[1] = (self.tête[0]-1 	+ self.têteOffset[0],  self.tête[1] 	+ self.têteOffset[1])
		def moveD():	self.rawMove[0], self.rawMove[1] = (self.tête[0]+1 	+ self.têteOffset[0],  self.tête[1] 	+ self.têteOffset[1])
		def moveH(): 	self.rawMove[0], self.rawMove[1] = (self.tête[0]   	+ self.têteOffset[0],  self.tête[1]-1 	+ self.têteOffset[1])
		def moveB():	self.rawMove[0], self.rawMove[1] = (self.tête[0]  	+ self.têteOffset[0],  self.tête[1]+1 	+ self.têteOffset[1])

		
		self.moveDict = {'G': moveG, 'D': moveD, 'H': moveH, 'B': moveB}						
		
		self.newCoord = 	{'normal': lambda: self.rawMove, 
							 'wrapAround': lambda: (self.rawMove[0] % self.grid_nbCols, self.rawMove[1] % self.grid_nbLigs)}
		self.rawfilter = 	 'normal' # Le filtre de mouvement à appliquer sur rawMove

		
		self.segmentsPool = 	sorted(list(self.can.find_withtag('Snake'))) # liste des itemIDs des segments servant à les déplacer
		#self.PowerUps_liste =	[self.PowerUp_mue, self.PowerUp_zigzag]
		
		self.noGoodDirs =	[{'H', 'B'}, {'D', 'G'}] # Illégal de passer de H à B ou de D à G.
		self.dirDict = 		{(0,1):'B',(0,-1):'H',(1,0):'D',(-1,0):'G'}
		
		self.failState_conditions = (lambda tête_: not (0 <= tête_[0] < self.grid_nbCols),
									 lambda tête_: not (0 <= tête_[1] < self.grid_nbLigs),
									 lambda tête_: tête_ in self.snake[:-3],
									 lambda tête_: tête_ in self.snake_peauMorte)
		
		self.failState_setup = 	(0,1,2,3) # Indexes failState_conditions actuellement vérifiées.
		# _GameLoop Utils


		# EventIDs_
		self.MainEvent = 0 # eventId pour la GameLoop
		self.Poof_timeoutEvent = 0
		self.timerEvent = 0
		# _EventIDs


		# Mr.Poof_
		self.Poof_congrats = {'WOW !', "Qui l'aurrait cru !", "SsSsSuper!", "Tu m'émousilles !", "Incroyable !"}
		self.PoofMessage = tk.StringVar()
		self.PoofMessage.set('')
		# _Mr.Poof


		# Vars tracing_
		self.gear.trace('w', 			self.gearShift)
		self.PoofMessage.trace('w', 	self.PoofDisplay)

		self.longueur.trace('w', 		self.UI_update)
		self.score_actuelle.trace('w', 	self.UI_update)
		self.temps_total.trace('w', 	self.UI_update)
		self.score_modif.trace('w',		self.total_modeDif)
		self.combo_modif.trace('w', 	self.total_modeDif)
		self.total_scoreModif.trace('w',self.UI_update)
		# _Vars tracing

		
		# UI_
		self.police, self.pol_size, self.pol_style = 'Ink Free', 12, 'bold italic'
		self.Highscore_size, self.Highscore_coul = 14, 'yellow'

		self.Gauge_updateRate = 200 # ms entre updates

		self.can.create_text(self.gridOffX + (self.grid.rangeX[1]-self.grid.rangeX[0])/2 , self.gridOffY + (self.grid.rangeY[1]-self.grid.rangeY[0])/2
			,text='PESEZ ENTER', anchor='center', fill='light green' , font=(self.police, 20, 'bold'), tags='TITLE')
					
		self.can.create_text(self.gridOffX+(self.gridLARG/2), self.gridOffY+(self.gridHAUT/2), text=self.PoofMessage.get() ,anchor='center', font=(self.police, 24, self.pol_style), fill='white', tags=['Poof','UI'])

		self.can.create_text(15, 90, text= f'TopScore\n   {self.TopScore}', anchor='w', font=(self.police, self.pol_size, self.pol_style), fill='white', tags=['TopScore', 'UI'])
		self.can.create_text(15, 160, text= f'TopLong\n    {self.TopLong}', anchor='w', font=(self.police, self.pol_size, self.pol_style), fill='white', tags=['TopLong','UI'])
		self.can.create_text(15, 230, text= f'TopTemps\n    {self.TopTemps}', anchor='w', font=(self.police, self.pol_size, self.pol_style), fill='white', tags=['TopTemps', 'UI'])
		self.can.create_text(15, 300, text= f'TopScore/sec\n    {self.TopScoreSec}', anchor='w', font=(self.police, self.pol_size, self.pol_style), fill='white', tags=['TopScoreSec', 'UI'])
		self.can.create_text(15, 370, text= f'TopCombo\n    {self.TopCombo}', anchor='w', font=(self.police, self.pol_size, self.pol_style), fill='white', tags=['TopCombo', 'UI'])
		#self.can.create_rectangle( self.gridOffX + 50, self.gridOffY + 100, self.gridOffX + self.gridLARG-50, self.gridOffY + self.gridHAUT-50, fill='dark blue', outline='black', state='normal', tags= 'HighScoreFrame')
		
		# HighScore Tableau_
		self.round_rectangle(self.gridOffX + 50, self.gridOffY + 50, self.gridOffX + self.gridLARG-50, self.gridOffY + self.gridHAUT-50, rayon=50, fill='dark blue', outline='yellow', tags= ['HighFrame', 'HighUI'])
		self.can.create_text(self.gridOffX+70, self.gridOffY+70, text= "\n".join('Highscores'), anchor='nw', font=(self.police, 16, self.pol_style), fill='white', state='normal', tags=['HighTitle', 'HighUI'])
		self.can.create_text(self.gridOffX+(self.gridLARG/2)+20, self.gridOffY+90, text= f'GAME OVER !', anchor='center', font=(self.police, 24, self.pol_style), fill='white', state='normal', tags=['GAMEOVER', 'HighUI'])

		self.can.create_text(self.gridOffX+120, self.gridOffY+140, text= 'Score', anchor='w', font=(self.police, self.Highscore_size, self.pol_style), fill='white', state='normal', tags=['HighScore', 'HighUI', 'HighTexte'])
		self.can.create_text(self.gridOffX+self.gridLARG-70, self.gridOffY+140, text= f'{self.TopScore}', anchor='e', justify='right', font=(self.police, self.Highscore_size, self.pol_style), fill='white', state='normal', tags=['HighScore', 'Num_HighScore', 'HighUI', 'HighTexte'])

		self.can.create_text(self.gridOffX+120, self.gridOffY+180, text= 'Longueur', anchor='w', font=(self.police, self.Highscore_size, self.pol_style), fill='white', state='normal', tags=['HighLong', 'HighUI', 'HighTexte'])
		self.can.create_text(self.gridOffX+self.gridLARG-70, self.gridOffY+180, text= f'{self.TopLong}', anchor='e', justify='right', font=(self.police, self.Highscore_size, self.pol_style), fill='white', state='normal', tags=['HighLong','Num_HighLong', 'HighUI', 'HighTexte'])

		self.can.create_text(self.gridOffX+120, self.gridOffY+220, text= 'Temps', anchor='w', font=(self.police, self.Highscore_size, self.pol_style), fill='white', state='normal', tags=['HighTemps', 'HighUI', 'HighTexte'])
		self.can.create_text(self.gridOffX+self.gridLARG-70, self.gridOffY+220, text= f'{self.TopTemps}', anchor='e', justify='right', font=(self.police, self.Highscore_size, self.pol_style), fill='white', state='normal', tags=['HighTemps', 'Num_HighTemps', 'HighUI', 'HighTexte'])

		self.can.create_text(self.gridOffX+120, self.gridOffY+260, text= 'Score/sec', anchor='w', font=(self.police, self.Highscore_size, self.pol_style), fill='white', state='normal', tags=['HighScoreSec', 'HighUI', 'HighTexte'])
		self.can.create_text(self.gridOffX+self.gridLARG-70, self.gridOffY+260, text= f'{self.TopScoreSec}', anchor='e', justify='right', font=(self.police, self.Highscore_size, self.pol_style), fill='white', state='normal', tags=['HighScoreSec', 'Num_HighScoreSec', 'HighUI', 'HighTexte'])

		self.can.create_text(self.gridOffX+120, self.gridOffY+300, text= 'Combo', anchor='w', font=(self.police, self.Highscore_size, self.pol_style), fill='white', state='normal', tags=['HighCombo', 'HighUI', 'HighTexte'])
		self.can.create_text(self.gridOffX+self.gridLARG-70, self.gridOffY+300, text= f'{self.TopCombo}', anchor='e', justify='right', font=(self.police, self.Highscore_size, self.pol_style), fill='white', state='normal', tags=['HighCombo', 'Num_HighCombo', 'HighUI', 'HighTexte'])

		self.can.move('HighTexte', 0, 10)
		self.can.itemconfig('HighUI', state='hidden')
		# _HighScore Tableau

		self.can.create_text(LARG-30, 30, text= f'Score\n {self.score_actuelle.get()}', anchor='e', font=(self.police, self.pol_size, self.pol_style), fill='white', tags=['score','UI'])
		self.can.create_text(LARG-120, 30, text= f'Long\n   {self.longueur.get()}', anchor='e',font=(self.police, self.pol_size, self.pol_style), fill='white', tags=['long','UI'])
		self.can.create_text(LARG-210, 30, text= f'Temps\n    {self.temps_total.get()}', anchor='e', font=(self.police, self.pol_size, self.pol_style), fill='white', tags=['temps','UI'])
		self.can.create_text(LARG-300, 30, text= f'Combos\n    {self.combo_modif.get()}', anchor='e', font=(self.police, self.pol_size, self.pol_style), fill='white', tags=['combos','UI'])

		self.can.create_text(180, 30, text= f'x{self.score_modif.get()}', anchor='w', font=(self.police, 30, self.pol_style), fill='white', tags=['mod','UI'])

		self.emptyGaugePx_Y, self.fullGaugePx_Y = HAUT-30, HAUT-30-self.gridHAUT
		self.Gauge1Base = (LARG-25, LARG-5) # coords X
		self.Gauge2Base = (self.gridOffX-25, self.gridOffX-5) # coords X
		self.fullGaugeLen = self.emptyGaugePx_Y - self.fullGaugePx_Y
		self.can.create_rectangle(self.Gauge1Base[0], self.emptyGaugePx_Y, self.Gauge1Base[1], self.fullGaugePx_Y, fill='beige', outline='green', tags='GaugeBack')
		self.can.create_rectangle(self.Gauge1Base[0], self.emptyGaugePx_Y, self.Gauge1Base[1], self.emptyGaugePx_Y-(self.fullGaugeLen*0.01), fill='blue', outline='dark green', tags='Gauge1')

		self.can.create_rectangle(self.Gauge2Base[0], self.emptyGaugePx_Y, self.Gauge2Base[1], self.fullGaugePx_Y, fill='beige', outline='green', tags='GaugeBack')
		self.can.create_rectangle(self.Gauge2Base[0], self.emptyGaugePx_Y, self.Gauge2Base[1], self.emptyGaugePx_Y-(self.fullGaugeLen*0.01), fill='light green', outline='dark green', tags='Gauge2')

		self.can.tag_raise('Poof')
		self.can.tag_raise('HighUI')

		self.HighUI_state = False
		# _UI

		self.scoreLabels_dump = []

		# Bindings_
		self.can.bind('<Left>', 		lambda event: self.directionChange('G'))
		self.can.bind('<Right>',		lambda event: self.directionChange('D'))
		self.can.bind('<Up>', 			lambda event: self.directionChange('H'))
		self.can.bind('<Down>', 		lambda event: self.directionChange('B'))
		self.can.bind('<Return>', 		self.StartGame_INIT)
		self.can.bind('<BackSpace>',	self.PauseGame)
		self.can.bind('<Delete>', 		self.RESET)

		self.can.bind('<KeyPress>', 	self.inputManager)	# Sert aux touches 1-9 pour gearShift
		self.can.bind('<KeyRelease>',	self.releaseManager)
		# _Bindings

		self.POW = 0 	# Placeholder pour entrer le nom de l'instance de PowerUps à la fin de Main  

	def round_rectangle(self, x1, y1, x2, y2, rayon=25, **kwargs):

	    points = [x1+rayon, y1,
	              #x1+rayon, y1,
	              x2-rayon, y1,
	             # x2-rayon, y1,
	              x2, y1,
	              x2, y1+rayon,
	              #x2, y1+rayon,
	              x2, y2-rayon,
	              #x2, y2-rayon,
	              x2, y2,
	              x2-rayon, y2,
	              #x2-rayon, y2,
	              x1+rayon, y2,
	              #x1+rayon, y2,
	              x1, y2,
	              x1, y2-rayon,
	              #x1, y2-rayon,
	              x1, y1+rayon,
	              #x1, y1+rayon,
	              x1, y1]

	    return self.can.create_polygon(points, **kwargs, smooth=True)


	def POW__init__(self, instance):
		self.POW = instance
		print('\ninstance de PowerUps :', self.POW)
		print("func PowerUp_gen de l'instance :", self.POW.PowerUp_Gen, '\n')
		

	def MainLoop(self):

		self.root.mainloop()



	def RESET(self, event):
		
		if self.GAMEOVER:
			self.can.delete('Snake')
			self.can.delete('PeauMorte')

			self.PoofMessage.set('')
			self.can.itemconfig('Poof', text= self.PoofMessage.get(), fill='white')
			self.can.itemconfig('PoofSet', fill='white')
			#self.can.itemconfig('UI', fill='white')	
			self.can.itemconfig('frame', outline='light blue')		
			self.can.itemconfig('gridBG', fill='black')
			self.can.itemconfig('Grid', fill='blue')

			self.can.itemconfig('HighTexte', font=(self.police, self.Highscore_size, self.pol_style), fill='white')
			self.can.itemconfig('HighUI', state='hidden')
			
			'''
			self.can.itemconfig('HighScore', text= f'Score 	         {self.TopScore}')
			self.can.itemconfig('HighLong', text= f'Longueur 	         {self.TopLong}')
			self.can.itemconfig('HighTemps', text= f'Temps 	         {self.TopTemps}')
			self.can.itemconfig('HighScoreSec', text= f'Score/sec 	         {self.TopScoreSec}')
			self.can.itemconfig('HighCombo', text= f'Combo 	         {self.TopCombo}')
			'''
			self.snake = [(1,1),(2,1)]
			self.snake_peauMorte = dict()
			self.tête = zeros(2,int)
			self.tête[0], self.tête[1] = self.snake[-1][0], self.snake[-1][1]
			self.têteOffset = zeros(2,int)
			self.têteOffset[0], self.têteOffset[1] = (0,0)
			self.pomme = zeros(2,int)
			self.pomme[0], self.pomme[1] = (rint(0,self.grid_nbCols-1), rint(0,self.grid_nbLigs-1))
			self.direction = 'D'



			# SCORES_
			self.longueur.set(len(self.snake))

			self.vitesse_Base = 500
			self.score_Base = 1000

			self.temps_total.set(0)
			self.temps_dernPomme = monotonic()

			self.score_Base = 1000
			self.score_actuelle.set(0)
			self.score_modif.set(1)

			self.combo_timer = 0
			self.combo_modif.set(1)
			
			# _SCORES>


			self.GameOn = True
			self.GAMEOVER = False

			self.POW.PowerUp_RESET()

			self.can.itemconfig('Pomme', fill='red')
			self.nouvelle_Pomme()

			self.segCoords_temp =  zeros((2,2), int) #[[0,0],[0,0]]	# espace réservé pour les coords du nouveau seg créé chaque gameLoop
			for segment in self.snake:

				self.segmentCoord(segment)
				self.can.create_rectangle(*self.segCoords_temp[0], *self.segCoords_temp[1], fill= self.snake_col, tags='Snake')

			self.MainEvent = 0
			self.segmentsPool = sorted(list(self.can.find_withtag('Snake')))
			
			self.can.coords('Gauge1', self.Gauge1Base[0], self.emptyGaugePx_Y, self.Gauge1Base[1], self.emptyGaugePx_Y)
			self.can.coords('Gauge2', self.Gauge2Base[0], self.emptyGaugePx_Y, self.Gauge2Base[1], self.emptyGaugePx_Y)

			self.HighUI_state = False
			self.can.bind('<BackSpace>', self.PauseGame)


			self.timer()
			self.GameLoop()


	def segmentCoord(self, index):
		NWCoord = self.grid.find_coord(index)
		self.segCoords_temp[0][0], self.segCoords_temp[0][1] = (NWCoord[0]+self.gridCell_10pX, NWCoord[1]+self.gridCell_10pY)
		self.segCoords_temp[1][0], self.segCoords_temp[1][1] = (NWCoord[0]+self.segLARG, NWCoord[1]+self.segHAUT)
		#coord1 = tuple([ c + self.gridCell_10pX  for c in self.grid.find_coord(index)])
		#coord2 = ( coord1[0] + self.grid.CellLARG-(2*self.gridCell_10pX), coord1[1] + self.grid.CellHAUT-(2*self.gridCell_10pX) )
		#return (coord1, coord2)


	def nouvelle_Pomme(self):
		while True:
			self.pomme[0], self.pomme[1] = (rint(0,self.grid_nbCols-1), rint(0,self.grid_nbLigs-1))
			if tuple(self.pomme) not in self.snake_peauMorte:
				break
		self.pommeCoord[0], self.pommeCoord[1] = self.grid.find_coord( self.pomme ) 
		self.can.coords('Pomme', self.pommeCoord[0]+self.gridCell_10pX, self.pommeCoord[1]+self.gridCell_10pY, self.pommeCoord[0]+self.grid.CellLARG-self.gridCell_10pX, self.pommeCoord[1]+self.grid.CellHAUT-self.gridCell_10pY)
		#print('Mem ID de pommeCoord',id(self.pommeCoord))
	


	def moveFilter(self): 
			self.moveDict[self.direction]()
			filtreCoord = self.newCoord[self.rawfilter]()
			self.filteredMove[0], self.filteredMove[1] = filtreCoord[0], filtreCoord[1]

	def directionChange(self, direct):
		testCoord = ((self.tête[0]-self.têteOffset[0])-self.snake[-2][0], (self.tête[1]-self.têteOffset[1])-self.snake[-2][1])
		#print(testCoord)
		try:				vraiDir = self.dirDict[testCoord]
		except KeyError:	return None

		if not ({vraiDir, direct} in self.noGoodDirs):
			self.direction = direct

		self.têteOffset[0], self.têteOffset[1] = (0,0)



	def GameLoop(self):
		#print(self.tête)
		try:				
			#self.tête = self.tête_calc_mode[] #self.moveDict[self.direction]()
			self.moveFilter()
			self.tête[0], self.tête[1] = self.filteredMove[0], self.filteredMove[1]
		except KeyError:	pass #return None

		tupTête = tuple(self.tête)
		self.snake += [tupTête]
		
		self.segmentCoord(tupTête)
		self.can.coords(self.segmentsPool[0], *self.segCoords_temp[0], *self.segCoords_temp[1] )

		self.segmentsPool += [self.segmentsPool.pop(0)] # flip le dernier segment en première place/ en self.tête.

		failState = False
		for cond_index in self.failState_setup:
			failState |= self.failState_conditions[cond_index](tupTête)

		if failState:
			print('Un bonne fessée !')
			self.GAMEOVER_procedure()
			return None
				
		#print('self.tête, snake_corps :',self.tête, self.snake[:-1])

		if tupTête == tuple(self.pomme):
			self.nouvelle_Pomme()
			self.longueur.set(self.longueur.get() + 1)

			self.PoofMessage.set(sample(self.Poof_congrats,1)[0])

			self.segmentCoord(self.snake[0])			
			self.segmentsPool.insert(0, self.can.create_rectangle(*self.segCoords_temp[0], *self.segCoords_temp[1], fill= self.snake_col, tags='Snake'))
			
			TIME = monotonic()
			depuis_dernPomme = TIME - self.temps_dernPomme
			self.temps_dernPomme = TIME

			self.combo_modif.set(self.combo_modif.get() + 1)
			self.combo_timer = self.combo_delay	# Reset le delay combo 

			scoreExtra = int(self.roundy( (self.score_Base * self.total_scoreModif.get()) / depuis_dernPomme, tol=-1) )
			self.score_actuelle.set( self.score_actuelle.get() + scoreExtra)
			self.scoreLabels_dump += [scoreLabels(scoreExtra, Game)]
			#print('combo_timerEvent :', self.combo_timerEvent)
			try:				self.can.after_cancel(self.combo_timerEvent)
			except ValueError: 	pass

			self.comboTimer()

			if rand() < self.PowerUp_chance: 
				print('PowerGen !')
				self.POW.PowerUp_Gen()

		else:
			self.snake.pop(0) # réduit de un à l'arrière et grandit de un à l'avant si pomme pas atrappé.


		if self.POW.PowerUp_onMap:
			#print('self.tête, self.PowerUp_coord :', self.tête, self.PowerUp_coord)

			if tupTête in POW:
				self.POW.PowerUp_instances[tupTête]['func'].activate()

		if not self.GAMEOVER:
			self.MainEvent = self.can.after(self.vitesse_actuelle, self.GameLoop) # Loop si pas GAMEOVER



	def PoofDisplay(self, *trace):
		message = self.PoofMessage.get()
	
		self.can.itemconfig('Poof', text=message, state='normal')

		try:					self.can.after_cancel(self.Poof_timeoutEvent)
		except ValueError:		pass

		self.Poof_timeoutEvent = self.can.after(1500, self.PoofClear)


	def PoofClear(self):
		self.can.itemconfig('Poof', state='hidden')
		self.Poof_timeoutEvent = 0
	


	def Score_addBonus(self, bonus):
		bonus = bonus * self.total_scoreModif.get()
		self.score_actuelle.set( self.score_actuelle.get() + bonus )
		self.scoreLabels_dump += [scoreLabels(bonus, Game)]

	def Score_addDelModif(self, modif, add=True ):
		# ajoute un multiplicateur si add=True sinon enlève le mult.
		if add:			self.score_modArray += [modif]
		else:			self.score_modArray.remove(modif)

		self.score_modif.set(sum(self.score_modArray))


	def StartGame(self, event):
		if self.MainEvent == 0 and not self.GAMEOVER:
			self.GameOn = True
			if self.combo_timerEvent != 0:
				self.combo_timerEvent = 0
				self.comboTimer()

			self.timer()
			self.GameLoop()

	def StartGame_INIT(self, event):

		self.can.delete('TITLE')
		self.can.itemconfig('Grid', state='normal')
		self.can.itemconfig('Snake', state='normal')
		self.can.itemconfig('Pomme', state='normal')

		self.GameOn = True
		self.can.bind('<Return>', self.StartGame)
		
		self.timer()
		self.GameLoop()

	def PauseGame(self, event):
		if self.GameOn:
			print('PAUSE!')
			try:
				self.can.after_cancel(self.MainEvent)
				self.can.after_cancel(self.timerEvent)
				self.can.after_cancel(self.combo_timerEvent)
			except ValueError:
				print('Event déjà anullé.' )

			self.MainEvent = 0
			self.timerEvent = 0
			self.GameOn = False

	def GAMEOVER_procedure(self):
		self.GAMEOVER = True
		self.PauseGame(0)
		self.POW.PowerUp_GAMEOVER_Procedure()

		try:	self.can.after_cancel(self.combo_timerEvent)
		except	ValueError: pass

		#self.PoofMessage.set('GAME OVER !')
		self.can.itemconfig('HighUI', state= 'normal')
		self.can.tag_raise('HighUI')
		
		self.can.itemconfig('gridBG', fill='white')
		self.can.itemconfig('Grid', fill='black')

		for item in self.can.find_withtag('Snake'):
			self.can.itemconfig(item, fill='black')

		self.can.itemconfig('Pomme', fill='black')
		#self.can.itemconfig('UI', fill='black')		
		self.can.itemconfig('frame', outline='red')		

		newTops = []
		if self.score_actuelle.get() > self.TopScore:
			newTops += ['TopScore']
			self.TopScore = self.score_actuelle.get()
			self.can.itemconfig('TopScore', text=f'TopScore\n   {self.TopScore}')
			self.can.itemconfig('HighScore', font=(self.police, int(self.Highscore_size*1.5), self.pol_style), fill= self.Highscore_coul)
			self.can.itemconfig('Num_HighScore', text= f'{self.TopScore}')

		if self.longueur.get() > self.TopLong:
			newTops += ['TopScore']
			self.TopLong = self.longueur.get()
			self.can.itemconfig('TopLong', text=f'TopLong\n   {self.TopLong}')
			self.can.itemconfig('HighLong', font=(self.police, int(self.Highscore_size*1.5), self.pol_style), fill= self.Highscore_coul)
			self.can.itemconfig('Num_HighLong', text=f'{self.TopLong}')

		if self.temps_total.get() > self.TopTemps:
			newTops += ['TopScore']
			self.TopTemps = self.temps_total.get()
			self.can.itemconfig('TopTemps', text=f'TopTemps\n   {self.TopTemps}')
			self.can.itemconfig('HighTemps', font=(self.police, int(self.Highscore_size*1.5), self.pol_style), fill= self.Highscore_coul)
			self.can.itemconfig('Num_HighTemps', text=f'{self.TopTemps}')

		scoreSec = int(self.score_actuelle.get() / self.temps_total.get())
		if scoreSec > self.TopScoreSec:
			newTops += ['TopScore']
			self.TopScoreSec = scoreSec
			self.can.itemconfig('TopScoreSec', text=f'TopScore/sec\n   {self.TopScoreSec}')
			self.can.itemconfig('HighScoreSec', font=(self.police, int(self.Highscore_size*1.5), self.pol_style), fill= self.Highscore_coul)
			self.can.itemconfig('Num_HighScoreSec', text=f'{self.TopScoreSec}')

		if self.combo_modif.get() > self.TopCombo:
			newTops += ['TopScore']
			self.TopCombo = self.combo_modif.get()
			self.can.itemconfig('TopCombo', text=f'TopCombo\n   {self.TopCombo}')
			self.can.itemconfig('HighCombo', font=(self.police, int(self.Highscore_size*1.5), self.pol_style), fill= self.Highscore_coul)
			self.can.itemconfig('Num_HighCombo', text=f'{self.TopCombo}')

		if newTops != []:
			with open('Snake_TopScores.txt', 'w') as TopFile:
				Tops = [f'TopScore={self.TopScore}\n',f'TopTemps={self.TopTemps}\n',f'TopLong={self.TopLong}\n',f'TopScoreSec={scoreSec}\n',f'TopCombo={self.TopCombo}']
				TopFile.writelines(Tops)

		self.can.bind('<BackSpace>', self.HighUI_flip)


	def inputManager(self, event):
		key = event.keysym
		print(key)
		try:
			
			self.gear.set(int(key))

		except ValueError:

			if key == 'Shift_L':
				self.quickSpeedChange(True, True)
			elif key == 'Control_L':
				self.quickSpeedChange(True, False)
			else:
				print(f'key {key} invalide')

	def releaseManager(self, event):
		key = event.keysym
		if key in ('Shift_L','Control_L'):
			self.quickSpeedChange(False)
		

	def gearShift(self, *trace):
		speedBase = self.vitesse_Base / self.gear.get()
		speedModded = self.speedMod[ self.speedMod_actu ]( speedBase )
		speedCapped = self.speedCap[ self.speedCap_actu ]( speedModded )
		self.vitesse_actuelle = int(speedCapped)

	def quickSpeedChange(self, actif, double=True):
		# si double est True double la vitesse si non divise par 2.
		if actif:
			if double:	self.speedMod_actu = 'double'
			else:		self.speedMod_actu = 'half'
		else:			self.speedMod_actu = 'normal'
		self.gearShift(None)
	

	def timer(self):
		tempT = self.temps_total.get()		
		self.temps_total.set(tempT + 1)

		if tempT % 10 == 0:
			self.vitesse_Base *= 0.95
			self.score_Base *= 1.05
			self.gearShift(None)

			# clear la dump des scoreLabels et del la ref de l'objet class à chaque 10 sec
			for i in range(len(self.scoreLabels_dump)-2):
				lab = self.scoreLabels_dump.pop(0)
				del lab

			
		self.timerEvent = self.can.after(1000, self.timer)


	def total_modeDif(self, *trace):
		# Calcule du multiplicateur total
		self.total_scoreModif.set(self.combo_modif.get() * self.score_modif.get())

	

	def comboTimer(self):
		
		Prop = self.combo_timer  / self.combo_delay
		self.can.coords('Gauge2', self.Gauge2Base[0], self.emptyGaugePx_Y, self.Gauge2Base[1], self.emptyGaugePx_Y-(self.fullGaugeLen * Prop))

		if self.combo_timer > 0:
			self.combo_timerEvent = self.can.after(self.Gauge_updateRate, self.comboTimer)
			self.combo_timer -= self.Gauge_updateRate
		else:
			self.combo_timerEvent = 0
			self.combo_modif.set(1)

	def UI_update(self, *trace):
		self.can.itemconfig('temps', text= 	f'Temps\n    {self.temps_total.get()}')
		self.can.itemconfig('score', text= 	f'Score\n    {self.score_actuelle.get()}')
		self.can.itemconfig('long', text= 	f'Longueur\n     {self.longueur.get()}')
		self.can.itemconfig('combos', text= 	f'Combos\n     {self.combo_modif.get()}')
		self.can.itemconfig('mod', text=	f'x{self.total_scoreModif.get()}')

	def HighUI_flip(self, event):
		# Montre ou cache le HighUI en GameOver avec Backspace
		self.HighUI_state ^= True # inverse et assigne
		if self.HighUI_state:
			self.can.itemconfig('HighUI', state= 'normal')
		else:
			self.can.itemconfig('HighUI', state= 'hidden')


if __name__ == '__main__':
	Game = wBob()
	config.snakeGame = Game
	
	class scoreLabels:
		vit, dist = 80, 20
		def __init__(self, score, master_):	
			self.master = master_
			self.itemID = self.master.can.create_text(*self.master.grid.find_coord(self.master.tête), text=str(score) , fill='white', font=(self.master.police, 20, self.master.pol_style))
			self.reps = 10
			self.anime()

		def anime(self):			
			self.master.can.move(self.itemID, 5, -self.dist)
			self.reps -= 1
			self.dist -= 2

			if self.reps > 0:		self.master.can.after(self.vit, self.anime)
			else:					self.master.can.delete(self.itemID)


	from PowerUps import PowerUps_class, PowerUp_mue, PowerUp_zigzag, PowerUp_wrapAround

	POW = PowerUps_class()
	Game.POW__init__(POW)

	#print('\nself :', POW)
	#print('testFunc :', POW.testFunc, '\n')
	
	#POW.testFunc()
	'''
	for i in getmembers(Game.POW):
		print(i)
	print(Game.POW.PowerUp_Gen)
	'''
	Game.MainLoop()