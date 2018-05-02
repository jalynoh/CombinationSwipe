import os, sys, time, random
import lib.Leap as Leap
from lib.Leap import CircleGesture, SwipeGesture
import pygame



'''
=============================================================
Resource_Path:
	- SOURCE: https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
	- Used to define path for pyInstaller
=============================================================
'''
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)



# PyGame globals
display_width = 800
display_height = 480
gameDisplay = pygame.display.set_mode((display_width, display_height), pygame.FULLSCREEN)
pygame.display.set_caption('Combo Swipe')
start_image = pygame.image.load(resource_path("assets\\start_image.png"))
bg = pygame.image.load(resource_path("assets\\background.png"))
finish_image = pygame.image.load(resource_path("assets\\finish_image.png"))
row_image = pygame.image.load(resource_path("assets\\row_selection.png"))
clock = pygame.time.Clock()
row1_Rect = [0, 44, 800, 100]
row2_Rect = [0, 189, 800, 100]
row3_Rect = [0, 334, 800, 100]

image_width = 100
white = (255, 255, 255)
black = (21, 21, 21)
green = (85, 107, 47)
red = (255, 0, 0)

# Leap Motion globals
controller = Leap.Controller() # Physical controller
lastFrameID = 0

leftPointBuffer = 0
rightPointBuffer = 0
thumbPointBuffer = 0

# Tracks the order of the rows
row1_Order = [1, 2, 3, 4, 5, 6, 7]
row2_Order = [1, 2, 3, 4, 5, 6, 7]
row3_Order = [1, 2, 3, 4, 5, 6, 7]
combo = [5, 2, 7]

'''
=============================================================
Leap Motion Listener:
	- provided leap motion class to handle intialization, connection, and disconnection of the physical Leap Motion
=============================================================
'''
class LeapMotionListener(Leap.Listener):

	def on_init(self, controller):
		print('Initialized!') # LATER: debug lines

	def on_connect(self, controller):
		print('Motion Sensor Connected!') # LATER: debug lines

		# Neccessary for gesture detection
		controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
		controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

	def on_disconnect(self, controller):
		print('Motion Sensor Disconnected!') # LATER: debug lines


def currentPoint():
	global lastFrameID

	global leftPointBuffer
	global rightPointBuffer
	global thumbPointBuffer

	maxBuffer = 10

	frame = controller.frame()
	if (frame.id == lastFrameID):
		return

	for hand in frame.hands:
		fingers = hand.fingers
		for pointable in hand.pointables:
			if ((pointable.id%10 == 0) and (pointable.is_extended)): # check last digit for 0 (thumb)
				thumbPointBuffer += 1
				if (thumbPointBuffer == maxBuffer):
					leftPointBuffer, rightPointBuffer, thumbPointBuffer = 0, 0, 0
					return('Thumb_Point')
			elif ((pointable.id%10 == 1) and (pointable.is_extended)): # Check last digit for 1 (index finger)
				if ((pointable.direction[0] <= -0.4)):
					leftPointBuffer += 1
					if (leftPointBuffer == maxBuffer):
						leftPointBuffer, rightPointBuffer, thumbPointBuffer = 0, 0, 0
						return('Left_Point')
				elif ((pointable.direction[0] >= 0.4)):
					rightPointBuffer += 1
					if (rightPointBuffer == maxBuffer):
						leftPointBuffer, rightPointBuffer, thumbPointBuffer = 0, 0, 0
						return('Right_Point')



'''
=============================================================
Current Gesture:
	- Leap motion handler
	- Detects if a new gesture has been performed since the last frame
=============================================================
'''
def currentGesture():
	global lastFrameID
	frame = controller.frame()
	if (frame.id == lastFrameID):
		return

	for gesture in frame.gestures():
		# CIRCLE
		if (gesture.type == Leap.Gesture.TYPE_CIRCLE):
			circle = CircleGesture(gesture)
			circlePerformed = 'Circle' if (circle.progress > 1) else 'False'
			print('Circle Performed?: ' + str(circlePerformed))
			if (circle.progress > 1):
				return('Circle')
			else:
				return

		# SWIPE
		elif (gesture.type == Leap.Gesture.TYPE_SWIPE):
			swipe = SwipeGesture(gesture)
			swipeDirection = 'Left_Swipe' if (swipe.direction[0] < 0) else 'Right_Swipe'
			print('Swipe Direction?: ' + swipeDirection)
			return(swipeDirection)



'''
=============================================================
Rotate Left & Rotate Right:
	- Shifts the rowOrder list around by 1
=============================================================
'''
def rotateLeft(row):
	global row1_Order, row2_Order, row3_Order

	if (row == 1):
		row1_Order = row1_Order[1:] + row1_Order[:1]
	elif (row == 2):
		row2_Order = row2_Order[1:] + row2_Order[:1]
	elif (row == 3):
		row3_Order = row3_Order[1:] + row3_Order[:1]

	print(row1_Order)
	print(row2_Order)
	print(row3_Order)
	


def rotateRight(row):
	global row1_Order, row2_Order, row3_Order

	if (row == 1):
		row1_Order = row1_Order[-1:] + row1_Order[:-1]
	elif (row == 2):
		row2_Order = row2_Order[-1:] + row2_Order[:-1]
	elif (row == 3):
		row3_Order = row3_Order[-1:] + row3_Order[:-1]
	
	print(row1_Order)
	print(row2_Order)
	print(row3_Order)


def displayRowSelection(row):
	if (row == '1'):
		gameDisplay.blit(row_image, ((display_width/2) - 65, 30))
	elif (row == '2'):
		gameDisplay.blit(row_image, ((display_width/2) - 65, 175))
	elif (row == '3'):
		gameDisplay.blit(row_image, ((display_width/2) - 65, 320))


'''
=============================================================
Load Images:
	- Loads images in from asset folder
=============================================================
'''
def loadImg(rowNumber, imgNumber, x, y):
	gameDisplay.blit(pygame.image.load(resource_path('assets\\row'+rowNumber+'_tile'+imgNumber+'.png')), (x, y))



'''
=============================================================
Display Combo Images:
	- Handles dislpaying the combos in the window
	- Displaying them in order according to the rowOrder array above, that changes on every swipe
=============================================================
'''
def displayComboImg(row, x, y):
	global row1_Order, row2_Order, row3_Order

	spacing = 0

	if (row == '1'):
		for i in row1_Order:
			loadImg(row, str(i), (x + spacing), y)
			spacing += 112.5

	elif (row == '2'):
		for i in row2_Order:
			loadImg(row, str(i), (x + spacing), y)
			spacing += 112.5

	elif (row == '3'):
		for i in row3_Order:
			loadImg(row, str(i), (x + spacing), y)
			spacing += 112.5



'''
=============================================================
Wrap Around Combo Image:
	- Gives the perception of an image wrapping around the screen when it hits the border
=============================================================
'''
def wrapAroundComboImg(row, x, y, apperance_side):
	global row1_Order, row2_Order, row3_Order

	if (row == '1'):
		if (apperance_side == 'Right_Border'):
			loadImg(row, str(row1_Order[0]), x, y)

		elif (apperance_side == 'Left_Border'):
			loadImg(row, str(row1_Order[6]), x, y)

	elif (row == '2'):
		if (apperance_side == 'Right_Border'):
			loadImg(row, str(row2_Order[0]), x, y)

		elif (apperance_side == 'Left_Border'):
			loadImg(row, str(row2_Order[6]), x, y)

	elif (row == '3'):
		if (apperance_side == 'Right_Border'):
			loadImg(row, str(row3_Order[0]), x, y)

		elif (apperance_side == 'Left_Border'):
			loadImg(row, str(row3_Order[6]), x, y)	


'''
=============================================================
Slide Combos:
	- Handles the sliding animation when a hand is swiped right or left
=============================================================
'''
def slideCombos(row, direction, x, y):

	if (direction == 'Left_Point'):
		for fps in range(112): # This range should corespond to how much the image is moving over
			gameDisplay.blit(bg, (0,0)) # Display background first
			displayComboImg(row, x - fps, y) # Displays regular comboImage

			# If the image hits the left border there will now also be a display
			# on the right side of the image wrapping around
			if ((x - fps) < 0):
				wrapAroundComboImg(row, display_width - fps, y, 'Right_Border')

			if (row == '1'):
				pygame.display.update(row1_Rect)
			elif (row == '2'):
				pygame.display.update(row2_Rect)
			elif (row == '3'):
				pygame.display.update(row3_Rect)

			pygame.time.delay(10)

	elif (direction == 'Right_Point'):
		for fps in range(112):
			gameDisplay.blit(bg, (0,0))
			displayComboImg(row, x + fps, y)

			# If the image hits the right border there will also be a display
			# on the left side of the image wrapping around
			if ((x + fps + display_width) > display_width):
				wrapAroundComboImg(row, fps - image_width, y, 'Left_Border')

			if (row == '1'):
				pygame.display.update(row1_Rect)
			elif (row == '2'):
				pygame.display.update(row2_Rect)
			elif (row == '3'):
				pygame.display.update(row3_Rect)

			pygame.time.delay(10)

	return(x)

def playSound(effect):
		pygame.mixer.music.load(resource_path("assets\\"+effect+".ogg"))
		pygame.mixer.music.set_volume(0.5)
		pygame.mixer.music.play()



'''
=============================================================
Game_Loop:
	- Handles the feedback and logic for the game
=============================================================
'''
def Game_Loop():
	# Row placement LATER: MAKE DYNAMIC
	row1_x = (display_width * 0.015625)
	row1_y = (display_height * 0.0937)
	row2_x = (display_width * 0.015625)
	row2_y = (display_height * 0.395833)
	row3_x = (display_width * 0.015625)
	row3_y = (display_height * 0.6979166)

	# Keeps track of which row the user is on
	row = 1

	# Main game loop
	gameExit = False
	while not gameExit:
		# Check to see if player "X" out of the game
		for event in pygame.event.get():
			if (event.type == pygame.QUIT):
				pygame.quit()
				exit()
			elif (event.type == pygame.KEYDOWN):
				if (event.key == pygame.K_ESCAPE):
					pygame.quit()
					exit()

		# Grabs the current gesture from the Leap
		currPoint = currentPoint()
		if (currPoint == 'Left_Point'): # --------------LEFT
			playSound('swipeEffect')
			if (row == 1):
				row1_x = slideCombos(str(row), 'Left_Point', row1_x, row1_y)
			elif (row == 2):
				row2_x = slideCombos(str(row), 'Left_Point', row2_x, row2_y)
			elif (row == 3):
				row3_x = slideCombos(str(row), 'Left_Point', row3_x, row3_y)

			rotateLeft(row)

		if (currPoint == 'Right_Point'): # --------------RIGHT
			playSound('swipeEffect')
			if (row == 1):
				row1_x = slideCombos(str(row), 'Right_Point', row1_x, row1_y)
			elif (row == 2):
				row2_x = slideCombos(str(row), 'Right_Point', row2_x, row2_y)
			elif (row == 3):
				row3_x = slideCombos(str(row), 'Right_Point', row3_x, row3_y)

			rotateRight(row)

		if (currPoint == 'Thumb_Point'):  # --------------CIRCLE
			playSound('row_down')
			if (row == 1):
				row = 2
			elif (row == 2):
				row = 3
			else:
				row = 1
			displayRowSelection(str(row))
			time.sleep(0.5)

		# Check if combination is correct then exit game
		if ((row1_Order[3] == 5) and (row2_Order[3] == 2) and (row3_Order[3] == 7)):
			gameDisplay.fill(white) # Fills background
			gameDisplay.blit(finish_image, (0,0))
			pygame.display.update()
			time.sleep(5)
			pygame.quit()
			exit()
			

		currGesture = 'None' # Reset current gesture

		gameDisplay.fill(white) # Fills background
		gameDisplay.blit(bg, (0,0))

		displayRowSelection(str(row))

		# Displays row
		displayComboImg('1', row1_x, row1_y)
		displayComboImg('2', row2_x, row2_y)
		displayComboImg('3', row3_x, row3_y)

		pygame.display.update() # Displays entire frame
		clock.tick(60) # FPS



'''
=============================================================
Main
=============================================================
'''
def main():
	#Leap motion setup
	listener = LeapMotionListener() # Listener to handle hand input data
	controller.add_listener(listener)
	pygame.init()
	pygame.mixer.init()
	pygame.mixer.Channel(0).play(pygame.mixer.Sound(resource_path("assets\\background_music.ogg")), loops = -1)

	#Pre game picture
	gameDisplay.fill(white) # Fills background
	gameDisplay.blit(start_image, (0,0))
	pygame.display.update()
	time.sleep(5)

	Game_Loop()



if __name__ == '__main__':
	main()