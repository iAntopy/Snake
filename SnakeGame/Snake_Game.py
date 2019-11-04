import tkinter as tk
from tkinter.constants import *
from random import randint as rint, random as rand, sample, choice
from time import sleep, time
from math import ceil

from .homeImports.GridClass import Grid


def wBob():

	root = tk.Tk()

	LARG, HAUT = 600, 480
	offX, offY = 100, 100
	root.geometry('{}x{}+{}+{}'.format(LARG, HAUT, offX, offY))

	can = tk.Canvas(root, width=LARG, height=HAUT, bg='black')
	can.pack(fill=BOTH)

	police, pol_size, pol_style = 'Ink Free', 12, 'bold italic'


	gridOffX, gridOffY = 150, 60 
	gridLARG, gridHAUT = LARG-gridOffX-30, HAUT-gridOffY-30
	gridCell_Dimention = (20,20)
	grid_nbCols , grid_nbLigs = int(gridLARG / gridCell_Dimention[0]), int(HAUT / gridCell_Dimention[1])

	print('grid_nbCols et grid_nbLigs :', grid_nbCols , grid_nbLigs)
	grid = Grid(gridLARG, gridHAUT, grid_nbCols, grid_nbLigs, offsetX=gridOffX, offsetY=gridOffY)
	
	# Pour dessiner les blocs du corps du serpent plus petit que la cellule.
	gridCell_10pX = grid.CellLARG*0.1 
	gridCell_10pY = grid.CellHAUT*0.1

	[ can.create_line(*grid.find_coord((col, 0)), *grid.find_coord((col, grid.nbLigs_)), fill='blue', width=2, state='hidden', tags='grid') for col in range(1, grid_nbCols)]
	[ can.create_line(*grid.find_coord((0, lig)), *grid.find_coord((grid.nbCols_, lig)), fill='blue', width=2, state='hidden', tags='grid') for lig in range(1, grid_nbLigs)]

	can.create_line(*grid.find_coord((0, 0)), 			*grid.find_coord((grid_nbCols, 0)),				fill='light blue', width=3, tags='frame')
	can.create_line(*grid.find_coord((grid_nbCols, 0)), *grid.find_coord((grid_nbCols, grid_nbLigs)), 	fill='light blue', width=3, tags='frame')
	can.create_line(*grid.find_coord((0, 0)), 			*grid.find_coord((0, grid_nbLigs)),				fill='light blue', width=3, tags='frame')
	can.create_line(*grid.find_coord((0, grid_nbLigs)), *grid.find_coord((grid_nbCols, grid_nbLigs)), 	fill='light blue', width=3, tags='frame')

	can.create_text(gridOffX + (grid.rangeX[1]-grid.rangeX[0])/2 , gridOffY + (grid.rangeY[1]-grid.rangeY[0])/2, 
					text='PESEZ ENTER', anchor='center', fill='light green' , font=(police, 20, 'bold'), tags='TITLE')
				

	roundy = lambda nb, tol=2: int(nb*(10**tol)+0.5)/(10**tol)

	snake = [(1,1),(2,1)]
	snake_peauMorte = []
	snake_col = 'light green'

	longueur = tk.IntVar(value=len(snake))

	tête = snake[-1]
	têteOffset = [0,0]
	pomme = [rint(0,grid_nbCols-1), rint(0,grid_nbLigs-1)]
	pommeCoord = [*grid.find_coord( pomme ) ]
	direction = 'D'

	PowerUp_onMap = False
	PowerUp_coord = [-1,-1]
	PowerUp_events = []

	gear = tk.IntVar(value=1)
	
	vitesse_Base = 500
	vitesse_actuelle = int(vitesse_Base / gear.get())


	temps_total = tk.IntVar(value=1)
	temps_dernPomme = time()

	score_Base = 1000
	score_actuelle = tk.IntVar(value=0)


	try:
		with open('Snake_TopScores.txt', 'r') as TopFile:	
			TopScore, TopTemps, TopLong, TopScoreSec = [ int(TopLig.split('=')[1].strip('\n')) for TopLig in TopFile.readlines()]

	except FileNotFoundError:

		TopScore = 0
		TopTemps = 0
		TopLong = 0	
		TopScoreSec = 0

	print('TopScoreSec :', TopScoreSec)
	GameOn = True
	GAMEOVER = False

	#Power-Up Shape
	def PowerUp_gen():
		nonlocal PowerUp_coord, PowerUp_onMap
		while True:
			PowerUp_coord[0], PowerUp_coord[1] = rint(0,grid_nbCols-1), rint(0,grid_nbLigs-1)
			tPow = tuple(PowerUp_coord)
			if tPow not in snake_peauMorte:
				break
		PowerUp_onMap = True
		print('PowerUp_coord, PowerUp_onMap :', PowerUp_coord, PowerUp_onMap)
		Shape_Base = (grid.find_coord(tPow), grid.find_coord((tPow[0]+1, tPow[1])))
		cL, cH = grid.CellLARG, grid.CellHAUT
		can.create_polygon(*Shape_Base[0], *Shape_Base[1], Shape_Base[0][0] + cL/2, Shape_Base[0][1] + cH, fill='yellow', tags='PowerUp')
		can.create_arc(Shape_Base[0][0] - cL/2, Shape_Base[0][1] - cH/2,Shape_Base[0][0] + cL*1.5, Shape_Base[0][1] + cH*1.5, outline='purple', start=0, extent=359.9, style='arc', width=2, tags='PowerUp')

	def PowerUp_wipe():
		nonlocal PowerUp_onMap
		print('PowerUp_coord, PowerUp_onMap :', PowerUp_coord, PowerUp_onMap)
		try:
			can.delete('PowerUp')
			PowerUp_onMap = False
		except ValueError:
			print('PowerUp déjà suprimé')

		
	def PowerUp_eventWipe():		
		for event in PowerUp_events:
			try:
				can.after_cancel(event)
			except ValueError:
				print('PowerUp_event dàjà suprimé')


	Poof_congrats = {'WOW !', "Qui l'aurrait cru !", "SsSsSuper!", "Tu m'émousilles !", "Incroyable !"}

	
	def RESET(event):
		nonlocal snake, longueur, tête, longueur, pomme, pommeCoord, direction, vitesse_Base, score_Base, GameOn, GAMEOVER, MainEvent
		nonlocal segmentsPool, snake_peauMorte, PowerUp_coord, PowerUp_onMap
		if GAMEOVER:
			can.delete('snake')

			PoofMessage.set('')
			can.itemconfig('Poof', text=PoofMessage.get(), font=(police, 24, pol_style), fill='white')
			can.itemconfig('PoofSet', fill='white')
			can.itemconfig('UI', fill='white')		
			can.config(bg='black')


			snake = [(1,1),(2,1)]
			snake_peauMorte = []
			longueur.set(len(snake))
			tête = snake[-1]
			pomme = [rint(0,grid_nbCols-1), rint(0,grid_nbLigs-1)]
			pommeCoord = [*grid.find_coord( pomme ) ]
			direction = 'D'

			PowerUp_onMap = False
			PowerUp_coord = [-1,-1]

			can.delete('PowerUp')

			vitesse_Base = 500
			score_Base = 1000

			temps_total.set(0)
			temps_dernPomme = time()

			score_actuelle.set(0)

			GameOn = True
			GAMEOVER = False

			can.itemconfig('pomme', fill='red')
			nouvelle_Pomme()

			for segment in snake:
				segCoord = segmentCoord(segment)
				can.create_rectangle(*segCoord[0], *segCoord[1], fill= snake_col, tags='snake')

			MainEvent = 0
			segmentsPool = sorted(list(can.find_withtag('snake')))

			timer()
			Main()


	def segmentCoord(index):
		coord1 = tuple([ c + gridCell_10pX  for c in grid.find_coord(index)])
		coord2 = ( coord1[0] + grid.CellLARG-(2*gridCell_10pX), coord1[1] + grid.CellHAUT-(2*gridCell_10pX) )
		return (coord1, coord2)


	def nouvelle_Pomme():
		nonlocal pomme, pommeCoord
		while True:
			pomme[0], pomme[1] = (rint(0,grid_nbCols-1), rint(0,grid_nbLigs-1))
			if tuple(pomme) not in snake_peauMorte:
				break
		pommeCoord[0], pommeCoord[1] = grid.find_coord( pomme ) 
		can.coords('pomme', pommeCoord[0]+gridCell_10pX, pommeCoord[1]+gridCell_10pY, pommeCoord[0]+grid.CellLARG-gridCell_10pX, pommeCoord[1]+grid.CellHAUT-gridCell_10pY)
	
	def zigzag(periode):
		# génère la sécance -1,0,0,1,1,0,0,-1, ...
		i = periode -1
		while True:
			Byte = '{0:03b}'.format( i )
			yield int(Byte[-2]) * (-1)**int(Byte[-3])
			i+=1

	
	for segment in snake:
		segCoord = segmentCoord(segment)
		can.create_rectangle(*segCoord[0], *segCoord[1], fill= snake_col, state='hidden' ,tags='snake')

	can.create_oval(pommeCoord[0]+gridCell_10pX, pommeCoord[1]+gridCell_10pY, pommeCoord[0]+grid.CellLARG-gridCell_10pX, pommeCoord[1]+grid.CellHAUT-gridCell_10pY,
	fill='red', outline='black', width=3, state='hidden' ,tags='pomme')
	


	moveDict = {'G': 	lambda: (tête[0]-1 + têteOffset[0],  tête[1] 	+ têteOffset[1]),	
				'D':	lambda: (tête[0]+1 + têteOffset[0],  tête[1] 	+ têteOffset[1]), 
				'H': 	lambda: (tête[0]   + têteOffset[0],  tête[1]-1 	+ têteOffset[1]),
				'B':	lambda: (tête[0]   + têteOffset[0],  tête[1]+1 	+ têteOffset[1])}



	MainEvent = 0
	segmentsPool = sorted(list(can.find_withtag('snake')))
	PowerUps_liste = [lambda: PowerUp_1, lambda: [ can.after(10000, PowerUp_eventWipe), PowerUp_zigzag()]]

	zzGen = zigzag(8)

	def PowerUp_1():
		nonlocal snake_peauMorte, segmentsPool, PowerUp_onMap, PowerUp_time

		midCut = longueur.get() / 2
		intMidCut = int(midCut)
		longueur.set(ceil(midCut))
		[snake_peauMorte.append(snake.pop(0)) for seg in range(intMidCut)]
		[segmentsPool.pop(0) for seg in range(intMidCut)]
		#snake_peauMorte += snake[:midCut]
		
		PowerUp_wipe()
		
	def PowerUp_zigzag():
		nonlocal têteOffset, PowerUp_events
		if direction in noGoodDirs[0]:
			#axe = 'Y'
			têteOffset[1] = next(zzGen)
		else:
			#axe = 'X'
			têteOffset[0] = next(zzGen)

		PowerUp_events.pop(-1)
		PowerUp_events += can.after(vitesse_actuelle, PowerUp_zigzag)
			
	def Main():
		nonlocal snake, tête, longueur, pomme, MainEvent, segmentsPool, GAMEOVER, temps_dernPomme, score_actuelle, PowerUp_onMap, PowerUp_time

		try:				tête = moveDict[direction]()
		except KeyError:	return None

		snake += [tête]
		
		newTête_Shape = segmentCoord(tête)
		can.coords(segmentsPool[0], *newTête_Shape[0], *newTête_Shape[1] )

		segmentsPool += [segmentsPool.pop(0)] # flip le dernier segment en première place/ en tête.

		if not (0 <= tête[0] < grid_nbCols) or not (0 <= tête[1] < grid_nbLigs) or tête in snake[:-1] or tête in snake_peauMorte:
			GAMEOVER_procedure()
			return None
				
		#print('tête, snake_corps :',tête, snake[:-1])

		if tête == tuple(pomme):
			nouvelle_Pomme()
			longueur.set(longueur.get() + 1)

			PoofMessage.set(sample(Poof_congrats,1)[0])

			segCoord = segmentCoord(snake[0])			
			segmentsPool.insert(0, can.create_rectangle(*segCoord[0], *segCoord[1], fill=snake_col, tags='snake'))
			
			TIME = time()
			depuis_dernPomme = TIME - temps_dernPomme
			temps_dernPomme = TIME

			score_actuelle.set( score_actuelle.get() + int(roundy(score_Base / depuis_dernPomme, tol=-1) ))
			
			
			if rand() < 0.3 and not PowerUp_onMap: 
				PowerUp_gen()
				can.after(10000, PowerUp_wipe)

		else:
			snake.pop(0)


		if PowerUp_onMap:
			#print('tête, PowerUp_coord :', tête, PowerUp_coord)
			if tête == tuple(PowerUp_coord):
				PowerUp_1()


		if not GAMEOVER:
			MainEvent = can.after(vitesse_actuelle, Main)


	noGoodDirs = [{'H', 'B'}, {'D', 'G'}]
	dirDict = {(0,1):'B',(0,-1):'H',(1,0):'D',(-1,0):'G'}
	def directionChange(direct):
		nonlocal direction
		vraiDir = dirDict[(tête[0]-snake[-2][0], tête[1]-snake[-2][1])]

		if not ({vraiDir, direct} in noGoodDirs):
			direction = direct


	Poof_timeoutEvent = 0
	def PoofDisplay(*trace):
		nonlocal Poof_timeoutEvent
		message = PoofMessage.get()
		if message == 'GAME OVER !':
			can.itemconfig('Poof', text=message, font=(police, 24, pol_style), state='normal', fill='black')
		else:
			can.itemconfig('Poof', text=message, state='normal')

			try:					can.after_cancel(Poof_timeoutEvent)
			except ValueError:		pass

			Poof_timeoutEvent = can.after(3000, PoofClear)

	def PoofClear():
		can.itemconfig('Poof', state='hidden')
		Poof_timeoutEvent = 0

	def StartGame(event):
		nonlocal GameOn
		if MainEvent == 0 and not GAMEOVER:
			GameOn = True
			timer()
			Main()

	def StartGame_INIT(event):
		nonlocal GameOn
		can.delete('TITLE')
		can.itemconfig('grid', state='normal')
		can.itemconfig('snake', state='normal')
		can.itemconfig('pomme', state='normal')
		GameOn = True
		can.bind('<Return>', StartGame)
		timer()
		Main()

	def PauseGame(event):
		nonlocal GameOn, MainEvent, timerEvent
		if GameOn:
			print('PAUSE!')
			can.after_cancel(MainEvent)
			can.after_cancel(timerEvent)

			MainEvent = 0
			timerEvent = 0
			GameOn = False

	def GAMEOVER_procedure():
		nonlocal GAMEOVER, TopScore, TopLong, TopTemps, TopScoreSec
		GAMEOVER = True
		PauseGame(0)
		PoofMessage.set('GAME OVER !')
		can.config(bg='white')

		for item in can.find_withtag('snake'):
			can.itemconfig(item, fill='black')

		can.itemconfig('pomme', fill='black')
		can.itemconfig('UI', fill='black')		


		newTop = False
		if score_actuelle.get() > TopScore:
			newTop = True
			TopScore = score_actuelle.get()
			can.itemconfig('TopScore', text=f'TopScore\n   {TopScore}')

		if longueur.get() > TopLong:
			newTop = True
			TopLong = longueur.get()
			can.itemconfig('TopLong', text=f'TopLong\n   {TopLong}')

		if temps_total.get() > TopTemps:
			newTop = True
			TopTemps = temps_total.get()
			can.itemconfig('TopTemps', text=f'TopTemps\n   {TopTemps}')

		scoreSec = int(score_actuelle.get() / temps_total.get())
		if scoreSec > TopScoreSec:
			newTop = True
			TopScoreSec = scoreSec
			can.itemconfig('TopScoreSec', text=f'TopScore/sec\n   {TopScoreSec}')

		if newTop:
			with open('Snake_TopScores.txt', 'w') as TopFile:
				Tops = [f'TopScore={TopScore}\n',f'TopTemps={TopTemps}\n',f'TopLong={TopLong}\n',f'TopScoreSec={scoreSec}\n']
				TopFile.writelines(Tops)


	def inputManager(event):
		key = event.char
		try:
			key = int(key)
			if key in range(1,10): #Soit [1,9]
				gear.set(key)

		except ValueError:
			raise ValueError(f'key {key} invalide')


	def gearShift(*trace):
		nonlocal vitesse_actuelle		
		vitesse_actuelle = int(vitesse_Base / gear.get())

	timerEvent = 0
	def timer():
		nonlocal temps_total, timerEvent, vitesse_Base, score_Base
		tempT = temps_total.get()		
		temps_total.set(tempT + 1)

		if tempT % 10 == 0:
			vitesse_Base *= 0.95
			score_Base *= 1.05
			gearShift(None)	

		timerEvent = can.after(1000, timer)

	def UI_update(*trace):
		can.itemconfig('temps', text= f'Temps\n    {temps_total.get()}')
		can.itemconfig('score', text= f'Score\n    {score_actuelle.get()}')
		can.itemconfig('long', text= f'Longueur\n   {longueur.get()}')

	PoofMessage = tk.StringVar()
	PoofMessage.set('')
	PoofMessage.trace('w', PoofDisplay)

	can.create_text(20, 30, text=PoofMessage.get() ,anchor='w', font=(police, 24, pol_style), fill='white', tags=['Poof','UI'])

	can.create_text(20, 90, text= f'TopScore\n   {TopScore}', anchor='w', font=(police, pol_size, pol_style), fill='white', tags=['TopScore', 'UI'])
	can.create_text(20, 160, text= f'TopLong\n    {TopLong}', anchor='w', font=(police, pol_size, pol_style), fill='white', tags=['TopLong','UI'])
	can.create_text(20, 230, text= f'TopTemps\n    {TopTemps}', anchor='w', font=(police, pol_size, pol_style), fill='white', tags=['TopTemps', 'UI'])
	can.create_text(20, 300, text= f'TopScore/sec\n    {TopScoreSec}', anchor='w', font=(police, pol_size, pol_style), fill='white', tags=['TopScoreSec', 'UI'])

	can.create_text(LARG-20, 30, text= f'Score\n    {score_actuelle.get()}', anchor='e', font=(police, pol_size, pol_style), fill='white', tags=['score','UI'])
	can.create_text(LARG-130, 30, text= f'Longueur\n    {longueur.get()}', anchor='e',font=(police, pol_size, pol_style), fill='white', tags=['long','UI'])
	can.create_text(LARG-280, 30, text= f'Temps\n    {temps_total.get()}', anchor='e', font=(police, pol_size, pol_style), fill='white', tags=['temps','UI'])

	can.focus_set()
	can.bind('<Left>', 	lambda event: directionChange('G'))
	can.bind('<Right>', lambda event: directionChange('D'))
	can.bind('<Up>', 	lambda event: directionChange('H'))
	can.bind('<Down>', 	lambda event: directionChange('B'))
	can.bind('<Return>', StartGame_INIT)
	can.bind('<BackSpace>', PauseGame)
	can.bind('<Delete>', RESET)

	can.bind('<KeyPress>', inputManager)
	gear.trace('w', gearShift)

	longueur.trace('w', UI_update)
	score_actuelle.trace('w', UI_update)
	temps_total.trace('w', UI_update)

	

	root.mainloop()

wBob()