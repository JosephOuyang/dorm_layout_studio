from cmu_graphics import *
from cmu_cpcs_utils import *
import copy

'''
Dorm Layout Studio (KEY FEATURES FOR GRADING)

Core design features

- Three preset layouts (Single/Double/Triple) 
  with doors, windows, and on-screen room dimensions 
  taken from real McGill House / Morewood Gardens floor plans.

- Furniture palette (bed/closet/desk): click + drag from the palette
  into the room to spawn new pieces (a simple click without dragging 
  will NOT keep the piece). 
  
- Clicking a piece in the room selects it; pressing 'r' rotates 
  the selected piece 90 degrees clockwise each time.
  
Placement feedback & validity

- While a piece is selected, a rectangular "ghost" outline is drawn:
  - Green = valid placement (inside room, no overlap with other furniture).
  - Red = invalid placement (outside room or overlapping).

- If you release in an invalid position:
  - Newly spawned furniture is removed.
  - Existing furniture snaps back to its original position, size, and orientation.

Measurement mode (RULER panel)

- Click the RULER panel (bottom-left) to toggle measurement mode (green border = ON).

- In measurement mode:
  - First click in the room sets the start point;
    second click sets the end point and saves a measurement segment.
  - Distances update continuously while moving the mouse and are 
    scaled to real-world inches/feet based on the current layout.
- Press 'esc' or click the small 'X' on the RULER panel to exit measurement mode.

Undo / Redo & Trash

- Undo /redo history tracks furniture moves, rotations, deletions, and measurement segments.
- Controls:
  - Keyboard: 'z' = Undo, 'y' = Redo
  - Buttons under "Back to Layouts": left arrow (Undo), right arrow (Redo);
    buttons are greyed out when unavailable
- Drag a furniture piece onto the trash can (bottom-right) and release to delete it;
  this action is also undoable

'''

################################################
# MODEL
################################################
    
def onAppStart(app):
    ################################################
    # IMAGES AND BACKGROUND
    ################################################
    
    # images (Source: ChatGPT Image Generator)
    app.bedImage = 'https://raw.githubusercontent.com/JosephOuyang/dorm_layout_studio/master/bed2.jpg'
    app.closetImage = 'https://raw.githubusercontent.com/JosephOuyang/dorm_layout_studio/master/closet2.jpg'
    app.deskImage = 'https://raw.githubusercontent.com/JosephOuyang/dorm_layout_studio/master/desk2.jpg'
    app.trashImage = 'https://raw.githubusercontent.com/JosephOuyang/dorm_layout_studio/master/trash.png'
    app.titleImage = 'https://raw.githubusercontent.com/JosephOuyang/dorm_layout_studio/master/title.png'
    app.singlePreviewImage = 'https://raw.githubusercontent.com/JosephOuyang/dorm_layout_studio/master/single_preview.png'
    app.doublePreviewImage = 'https://raw.githubusercontent.com/JosephOuyang/dorm_layout_studio/master/double_preview.png'
    app.triplePreviewImage = 'https://raw.githubusercontent.com/JosephOuyang/dorm_layout_studio/master/triple_preview.png'
    app.rulerImage = 'https://raw.githubusercontent.com/JosephOuyang/dorm_layout_studio/master/ruler2.png'
    
    # background color
    app.background = rgb(254, 247, 232)
    
    ################################################
    # HOME SCREEN BUTTON
    ################################################
    
    # home screen
    app.buttonWidth = 220
    app.buttonHeight = 60
    app.buttonLeft = app.width / 2 - app.buttonWidth / 2
    app.buttonTop = app.height / 2 + 100
    
    ################################################
    # LAYOUT SCREEN BUTTONS
    ################################################
    
    # layout select screen buttons
    app.layoutButtonWidth = 260
    app.layoutButtonHeight = 50
    
    # vertical coordinate
    buttonCenterY = app.height / 2 + 200
    app.layoutButtonTop = buttonCenterY - app.layoutButtonHeight / 2
    
    # single button
    singleCenterX = app.width / 4
    app.singleButtonLeft = singleCenterX - app.layoutButtonWidth / 2
    app.singleButtonTop = app.layoutButtonTop
    
    # double button
    doubleCenterX = app.width / 2
    app.doubleButtonLeft = doubleCenterX - app.layoutButtonWidth / 2
    app.doubleButtonTop = app.layoutButtonTop
    
    # triple button
    tripleCenterX = 3 * app.width / 4
    app.tripleButtonLeft = tripleCenterX - app.layoutButtonWidth / 2
    app.tripleButtonTop = app.layoutButtonTop
   
    # preview images above each layout button
    app.layoutPreviewWidth = 220
    app.layoutPreviewGap = 20
    
    ################################################
    # DESIGN SCREEN BUTTONS
    ################################################
   
    # design screen "Back to Home" button
    app.backButtonWidth = app.buttonWidth
    app.backButtonHeight = app.buttonHeight
    app.backButtonLeft = 20
    app.backButtonTop = 20
    
    # undo / redo buttons
    app.undoButtonSize = app.buttonHeight
    app.undoButtonLeft = app.backButtonLeft
    app.undoButtonTop = app.backButtonTop + app.backButtonHeight + 10
    
    app.redoButtonSize = app.undoButtonSize
    app.redoButtonLeft = app.undoButtonLeft + app.undoButtonSize + 10
    app.redoButtonTop = app.undoButtonTop
    
    ################################################
    # ROOM LAYOUTS
    ################################################
    
    # initialize room with dummy values
    app.room = Room(0, 0, 0, 0, (0, 0, 0, 0), [])
    
    # deafult single room dimensions
    app.singleRoomLeft = 300
    app.singleRoomTop = 130
    app.singleRoomWidth = 420
    app.singleRoomHeight = 290
    
    # default double room dimensions
    app.doubleRoomLeft = 300
    app.doubleRoomTop = 100
    app.doubleRoomWidth = 420
    app.doubleRoomHeight = 500
    
    # default triple room dimensions
    app.tripleRoomLeft = 300
    app.tripleRoomTop = 100
    app.tripleRoomWidth = 650
    app.tripleRoomHeight = 400
    
    # door/window sizes (shared)
    app.doorWidth = 70
    app.doorHeight = 2
    app.windowMargin = 20
    app.windowWidth = 80
    app.windowHeight = 2
    
    # furniture dimensions (shared)
    app.bedWidth = 120
    app.bedHeight = 220
    app.closetWidth = 100
    app.closetHeight = 50
    app.deskWidth = 70
    app.deskHeight = 40
    
    ################################################
    # PALETTE AND TRASH
    ################################################
    
    # palette
    app.paletteItems = [
        {
            'kind' : 'bed',
            'image' : app.bedImage,
            'width' : 120,
            'height' : 220
        },
        {
            'kind' : 'closet',
            'image' : app.closetImage,
            'width': app.closetWidth,
            'height' : app.closetHeight
        },
        {
            'kind' : 'desk',
            'image' : app.deskImage,
            'width' : 70,
            'height' : 40
        }
    ]
    
    app.paletteWidth = 140
    app.paletteHeight = 160
    app.paletteLeft = app.width - app.paletteWidth
    app.paletteTop = 100
    app.paletteSpacing = 160
    
    # trash bin (bottom-right)
    
    app.trashSize = 100
    app.trashLeft = app.width - app.trashSize - 20
    app.trashTop = app.height - app.trashSize - 20
    
    ################################################
    # MOVEMENT
    ################################################
    
    # ghost image
    app.ghostIsValid = True
    
    # below is to remedy janky movement when rotating pieces
    app.lastMouseX = None
    app.lastMouseY = None
    
    # mouse position for hover effects
    app.mouseX = None
    app.mouseY = None
    
    # hover state for door/windows
    app.hoverDoor = False
    app.hoverWindowIndex = None
    
    ################################################
    # DIMENSION LINES 
    ################################################
    
    app.currentLayout = None
    
    # (Source: McGill House Floor Plan)
    app.singleWidthLabel = '''12' 11"''' 
    app.singleHeightLabel = '''8' 7"'''
    
    app.doubleWidthLabel = '''11' 11"'''
    app.doubleHeightLabel = '''14' 3"'''
    
    # (Source: Morewood Gardens Floor Plan)
    app.tripleWidthLabel = '''24' 10"'''
    app.tripleHeightLabel = '''12' 9"'''
    
    ################################################
    # RULER/MEASURE MODE 
    ################################################
    
    app.measureMode = False
    app.measureStart = None
    app.measureTempEnd = None
    app.measureSegments = []
    
    app.lastMeasureHintSegmentIndex = None
    app.showMeasureEscHint = False
    
    app.measurePanelWidth = app.paletteWidth
    app.measurePanelHeight = app.paletteHeight
    app.measurePanelLeft = 20
    app.measurePanelTop = app.height - app.measurePanelHeight - 20
    app.measureCloseSize = 16
    
    ################################################
    # UNDO / REDO HISTORY 
    ################################################
    
    app.history = []
    app.redoStack = []
    app.didDrag = False
    
##########################################
# LAYOUT HELPERS
##########################################
    
def loadSingleLayout(app):
    # clears room, then load default single room
    app.room.furnitureList = []
    app.currentLayout = 'single'
    
    app.room.roomLeft = app.singleRoomLeft
    app.room.roomTop = app.singleRoomTop
    app.room.roomWidth = app.singleRoomWidth
    app.room.roomHeight = app.singleRoomHeight
    
    roomLeft = app.room.roomLeft
    roomTop = app.room.roomTop
    roomWidth = app.room.roomWidth
    roomHeight = app.room.roomHeight
    
    app.doorLeft = roomLeft + roomWidth - app.doorWidth
    app.doorTop = roomTop + roomHeight - app.doorHeight
    app.room.doorRect = (app.doorLeft, app.doorTop, app.doorWidth, app.doorHeight)
    
    app.room.windowRects = [(roomLeft + roomWidth - app.windowWidth - app.windowMargin, 
                        roomTop, app.windowWidth, app.windowHeight)]
    
    # beds
    bedLeft = roomLeft 
    bedTop = roomTop + 2
    bed = Furniture('bed', bedLeft, bedTop, app.bedWidth, app.bedHeight,
                    image = app.bedImage, angle = 0)
    app.room.addFurniture(bed)
    
    # closets
    closetLeft = roomLeft + 175
    closetTop = roomTop + 2
    closet = Furniture('closet', closetLeft, closetTop, app.closetWidth,
                        app.closetHeight, image = app.closetImage, angle = 0)
    app.room.addFurniture(closet)
    
    # desks
    deskLeft = 625
    deskTop = 132
    desk = Furniture('desk', deskLeft, deskTop, app.deskWidth, app.deskHeight,
                      image = app.deskImage, angle = 0)
    app.room.addFurniture(desk)  
    
    # reset history upon entering initial state
    app.history = []
    app.redoStack = []
    registerAction(app)
    
def loadDoubleLayout(app):
    # clears room, then load default double room
    app.room.furnitureList = []
    app.currentLayout = 'double'
    
    app.room.roomLeft = app.doubleRoomLeft
    app.room.roomTop = app.doubleRoomTop
    app.room.roomWidth = app.doubleRoomWidth
    app.room.roomHeight = app.doubleRoomHeight
    
    roomLeft = app.room.roomLeft
    roomTop = app.room.roomTop
    roomWidth = app.room.roomWidth
    roomHeight = app.room.roomHeight
    
    app.doorLeft = roomLeft + roomWidth - app.doorWidth
    app.doorTop = roomTop + roomHeight - app.doorHeight
    app.room.doorRect = (app.doorLeft, app.doorTop, app.doorWidth, app.doorHeight)
    
    app.room.windowRects = [(roomLeft + app.windowMargin, roomTop, app.windowWidth, app.windowHeight), 
                       (roomLeft + roomWidth - app.windowWidth - app.windowMargin, 
                        roomTop, app.windowWidth, app.windowHeight)]
    
    # beds
    bedLeft1 = roomLeft
    bedTop1 = roomTop + roomHeight - app.bedHeight
    bed1 = Furniture('bed', bedLeft1, bedTop1, app.bedWidth, app.bedHeight,
                     image = app.bedImage, angle = 180)
                     
    bedLeft2 = roomLeft + roomWidth - app.bedWidth
    bedTop2 = roomTop + app.windowHeight
    bed2 = Furniture('bed', bedLeft2, bedTop2, app.bedWidth, app.bedHeight, image = app.bedImage, angle = 0)
    
    app.room.addFurniture(bed1)
    app.room.addFurniture(bed2)
    
    # closets
    closetLeft1 = roomLeft + 227
    closetTop1 = 548
    closet1 = Furniture('closet', closetLeft1, closetTop1, app.closetWidth,
                        app.closetHeight, image = app.closetImage, angle = 180)
    closetLeft2 = roomLeft + 108
    closetTop2 = 102
    closet2 = Furniture('closet', closetLeft2, closetTop2, app.closetWidth,
                        app.closetHeight, image = app.closetImage, angle = 0)
                        
    app.room.addFurniture(closet1)
    app.room.addFurniture(closet2)
    
    # desks
    deskLeft1 = roomLeft + 140
    deskTop1 = 558
    desk1 = Furniture('desk', deskLeft1, deskTop1, app.deskWidth, app.deskHeight,
                      image = app.deskImage, angle = 0)
    deskLeft2 = roomLeft + 220
    deskTop2 = 102
    desk2 = Furniture('desk', deskLeft2, deskTop2, app.deskWidth, app.deskHeight,
                      image = app.deskImage, angle = 0)
                      
    app.room.addFurniture(desk1)
    app.room.addFurniture(desk2)
    
    # reset history upon entering initial state
    app.history = []
    app.redoStack = []
    registerAction(app)
    
def loadTripleLayout(app):
    # clears room, then load default triple room
    app.room.furnitureList = []
    app.currentLayout = 'triple'
    
    app.room.roomLeft = app.tripleRoomLeft
    app.room.roomTop = app.tripleRoomTop
    app.room.roomWidth = app.tripleRoomWidth
    app.room.roomHeight = app.tripleRoomHeight
    
    roomLeft = app.room.roomLeft
    roomTop = app.room.roomTop
    roomWidth = app.room.roomWidth
    roomHeight = app.room.roomHeight
    
    app.doorLeft = roomLeft + roomWidth - app.doorWidth
    app.doorTop = roomTop
    app.room.doorRect = (app.doorLeft, app.doorTop, app.doorWidth, app.doorHeight)
    
    app.room.windowRects = [(440, roomTop + roomHeight - app.windowHeight, app.windowWidth, app.windowHeight), 
                       (720, roomTop + roomHeight - app.windowHeight, app.windowWidth, app.windowHeight)]
    
    # beds
    bedLeft1 = roomLeft
    bedTop1 = roomTop + roomHeight - app.bedHeight
    bed1 = Furniture('bed', bedLeft1, bedTop1, app.bedWidth, app.bedHeight,
                     image = app.bedImage, angle = 180)
                     
    bedLeft2 = roomLeft + roomWidth / 2 - app.bedWidth / 2
    bedTop2 = roomTop + roomHeight - app.bedHeight
    bed2 = Furniture('bed', bedLeft2, bedTop2, app.bedWidth, app.bedHeight, image = app.bedImage, angle = 180)
    
    bedLeft3 = roomLeft + roomWidth - app.bedWidth
    bedTop3 = roomTop + roomHeight - app.bedHeight
    bed3 = Furniture('bed', bedLeft3, bedTop3, app.bedWidth, app.bedHeight, image = app.bedImage, angle = 180)
    
    app.room.addFurniture(bed1)
    app.room.addFurniture(bed2)
    app.room.addFurniture(bed3)
    
    # closets
    closetLeft1 = 320
    closetTop1 = roomTop + 2
    closet1 = Furniture('closet', closetLeft1, closetTop1, app.closetWidth,
                        app.closetHeight, image = app.closetImage, angle = 0)
    closetLeft2 = 520
    closetTop2 = roomTop + 2
    closet2 = Furniture('closet', closetLeft2, closetTop2, app.closetWidth,
                        app.closetHeight, image = app.closetImage, angle = 0)
         
    closetLeft3 = 705
    closetTop3 = roomTop + 2
    closet3 = Furniture('closet', closetLeft3, closetTop3, app.closetWidth,
                        app.closetHeight, image = app.closetImage, angle = 0)    
                        
    app.room.addFurniture(closet1)
    app.room.addFurniture(closet2)
    app.room.addFurniture(closet3)
    
    # desks
    deskLeft1 = 445
    deskTop1 = roomTop + roomHeight - app.deskHeight - app.windowHeight
    desk1 = Furniture('desk', deskLeft1, deskTop1, app.deskWidth, app.deskHeight,
                      image = app.deskImage, angle = 0)
    deskLeft2 = 725
    deskTop2 = roomTop + roomHeight - app.deskHeight - app.windowHeight
    desk2 = Furniture('desk', deskLeft2, deskTop2, app.deskWidth, app.deskHeight,
                      image = app.deskImage, angle = 0)
                      
    app.room.addFurniture(desk1)
    app.room.addFurniture(desk2)
    
    # reset history upon entering initial state
    app.history = []
    app.redoStack = []
    registerAction(app)
    
##########################################
# HOME SCREEN
##########################################

def home_redrawAll(app):
    drawImage(app.titleImage, app.width / 2, app.height / 2 - 50, width = app.width / 2, height = app.height * 0.75, align = 'center')
    
    # hover detection
    isHovering = (app.mouseX != None 
                  and isInsideRect(app.mouseX, app.mouseY, app.buttonLeft, app.buttonTop,
                  app.buttonWidth, app.buttonHeight))
    borderColor = 'gold' if isHovering else 'black'
    borderWidth = 4 if isHovering else 2
    
    drawRect(app.buttonLeft, app.buttonTop, app.buttonWidth, app.buttonHeight,
             fill = 'darkSlateBlue', border = borderColor, borderWidth = borderWidth)
    drawLabel("Let's Design!", app.width / 2, app.buttonTop + app.buttonHeight / 2,
              size = 22, bold = True, fill = 'white', font = 'monospace')
              
def home_onMousePress(app, mX, mY):
    buttonRight = app.buttonLeft + app.buttonWidth
    buttonBottom = app.buttonTop + app.buttonHeight
    if (app.buttonLeft <= mX <= buttonRight
        and app.buttonTop <= mY <= buttonBottom):
        setActiveScreen('layoutSelect')
        
def home_onMouseMove(app, mX, mY):
    app.mouseX = mX
    app.mouseY = mY

##########################################
# SELECT SCREEN
##########################################

def layoutSelect_redrawAll(app):
    drawRect(app.width / 2, 120, app.buttonWidth + 90, app.buttonHeight + 30, align = 'center', fill = 'gray', border = 'black')
    drawLabel('Choose A Layout', app.width / 2, 120, size = 32, bold = True, font = 'monospace', fill = 'white')
    
    # preview width and height (shared)
    previewWidth = app.layoutPreviewWidth
    previewHeight = 5 * app.layoutButtonHeight
    
    # single preview image
    singlePreviewCenterX = app.singleButtonLeft + app.layoutButtonWidth / 2
    singlePreviewCenterY = (app.singleButtonTop - app.layoutPreviewGap
                            - previewHeight / 2)
    
    drawImage(app.singlePreviewImage, singlePreviewCenterX,
              singlePreviewCenterY, width = previewWidth, height = previewHeight * 3 / 5, align = 'center')
    
    # double preview image
    doublePreviewCenterX = app.doubleButtonLeft + app.layoutButtonWidth / 2
    doublePreviewCenterY = (app.doubleButtonTop - app.layoutPreviewGap
                            - previewHeight / 2)
                            
    drawImage(app.doublePreviewImage, doublePreviewCenterX,
              doublePreviewCenterY, width = previewWidth, height = previewHeight, align = 'center')
    
    # triple preview image
    triplePreviewCenterX = app.tripleButtonLeft + app.layoutButtonWidth / 2
    triplePreviewCenterY = (app.tripleButtonTop - app.layoutPreviewGap
                            - previewHeight / 2)
                            
    drawImage(app.triplePreviewImage, triplePreviewCenterX,
              triplePreviewCenterY, width = previewWidth, height = previewHeight * 3 / 5, align = 'center')
     
    # hover states for buttons
    isSingleHovering = (app.mouseX != None and isInsideRect(app.mouseX, app.mouseY,
                        app.singleButtonLeft, app.singleButtonTop, app.layoutButtonWidth,
                        app.layoutButtonHeight))
                        
    isDoubleHovering = (app.mouseX != None and isInsideRect(app.mouseX, app.mouseY,
                        app.doubleButtonLeft, app.doubleButtonTop, app.layoutButtonWidth,
                        app.layoutButtonHeight))
    
    isTripleHovering = (app.mouseX != None and isInsideRect(app.mouseX, app.mouseY,
                        app.tripleButtonLeft, app.tripleButtonTop, app.layoutButtonWidth,
                        app.layoutButtonHeight))  
    
    isBackHovering = (app.mouseX != None and isInsideRect(app.mouseX, app.mouseY,
                        app.backButtonLeft, app.backButtonTop, app.layoutButtonWidth,
                        app.layoutButtonHeight))  
           
    # single
    drawRect(app.singleButtonLeft, app.singleButtonTop, app.layoutButtonWidth,
             app.layoutButtonHeight, fill = 'darkSlateBlue', 
             border = 'gold' if isSingleHovering else 'black', 
             borderWidth = 4 if isSingleHovering else 2)
    drawLabel('Single', app.singleButtonLeft + app.layoutButtonWidth / 2,
              app.singleButtonTop + app.layoutButtonHeight / 2,
              size = 20, bold = True, fill = 'white', font = 'monospace')
              
    # double
    drawRect(app.doubleButtonLeft, app.doubleButtonTop, app.layoutButtonWidth,
             app.layoutButtonHeight, fill = 'darkSlateBlue', 
             border = 'gold' if isDoubleHovering else 'black', 
             borderWidth = 4 if isDoubleHovering else 2)
    drawLabel('Double', app.doubleButtonLeft + app.layoutButtonWidth / 2,
              app.doubleButtonTop + app.layoutButtonHeight / 2,
              size = 20, bold = True, fill = 'white', font = 'monospace')
    
    # triple
    drawRect(app.tripleButtonLeft, app.tripleButtonTop, app.layoutButtonWidth,
             app.layoutButtonHeight, fill = 'darkSlateBlue', 
             border = 'gold' if isTripleHovering else 'black', 
             borderWidth = 4 if isTripleHovering else 2)
    drawLabel('Triple', app.tripleButtonLeft + app.layoutButtonWidth / 2,
              app.tripleButtonTop + app.layoutButtonHeight / 2,
              size = 20, bold = True, fill = 'white', font = 'monospace')
              
    # back to home button
    drawRect(app.backButtonLeft, app.backButtonTop, app.backButtonWidth,
             app.backButtonHeight, fill = 'darkSlateBlue', 
             border = 'gold' if isBackHovering else 'black',
             borderWidth = 4 if isBackHovering else 2)
    drawLabel('Back to Home', app.backButtonLeft + app.backButtonWidth / 2,
              app.backButtonTop + app.backButtonHeight / 2,
              size = 20, bold = True, fill = 'white', font = 'monospace')
              
def layoutSelect_onMousePress(app, mX, mY):
    backRight = app.backButtonLeft + app.backButtonWidth
    backBottom = app.backButtonTop + app.backButtonHeight
    if (app.backButtonLeft <= mX <= backRight and
        app.backButtonTop <= mY <= backBottom):
        app.room.selectedFurniture = None
        app.ghostIsValid = True
        setActiveScreen('home')
        return None
    # single button bounds
    singleRight = app.singleButtonLeft + app.layoutButtonWidth
    singleBottom = app.singleButtonTop + app.layoutButtonHeight
    
    # double button bounds
    doubleRight = app.doubleButtonLeft + app.layoutButtonWidth
    doubleBottom = app.doubleButtonTop + app.layoutButtonHeight
        
    # triple button bounds
    tripleRight = app.tripleButtonLeft + app.layoutButtonWidth
    tripleBottom = app.tripleButtonTop + app.layoutButtonHeight
    
    # single dorm
    if (app.singleButtonLeft <= mX <= singleRight and
        app.singleButtonTop <= mY <= singleBottom):
        loadSingleLayout(app)
        setActiveScreen('design')
        return None
    
    # double dorm
    if (app.doubleButtonLeft <= mX <= doubleRight and
        app.doubleButtonTop <= mY <= doubleBottom):
        loadDoubleLayout(app)
        setActiveScreen('design')
        return None
        
    # triple dorm
    if (app.tripleButtonLeft <= mX <= tripleRight and
        app.tripleButtonTop <= mY <= tripleBottom):
        loadTripleLayout(app)
        setActiveScreen('design')
        return None
        
def layoutSelect_onMouseMove(app, mX, mY):
    app.mouseX = mX
    app.mouseY = mY
    
##########################################
# DESIGN SCREEN
##########################################

def design_onMousePress(app, mX, mY):
    backRight = app.backButtonLeft + app.backButtonWidth
    backBottom = app.backButtonTop + app.backButtonHeight
    if (app.backButtonLeft <= mX <= backRight and
        app.backButtonTop <= mY <= backBottom):
        app.room.selectedFurniture = None
        app.ghostIsValid = True
        
        app.measureMode = False
        app.measureStart = None
        app.measureTempEnd = None
        app.measureSegments = []
        app.lastMeasureHintSegmentIndex = None
        app.showMeasureEscHint = False
        
        setActiveScreen('layoutSelect')
        return None
        
    # undo / redo buttons
    undoRight = app.undoButtonLeft + app.undoButtonSize
    undoBottom = app.undoButtonTop + app.undoButtonSize
    if (app.undoButtonLeft <= mX <= undoRight and 
        app.undoButtonTop <= mY <= undoBottom):
        undoAction(app)
        return None
        
    redoRight = app.redoButtonLeft + app.redoButtonSize
    redoBottom = app.redoButtonTop + app.redoButtonSize
    if (app.redoButtonLeft <= mX <= redoRight and 
        app.redoButtonTop <= mY <= redoBottom):
        redoAction(app)
        return None
        
    # measure mode behavior
    panelLeft = app.measurePanelLeft
    panelTop = app.measurePanelTop
    panelWidth = app.measurePanelWidth
    panelHeight = app.measurePanelHeight
    
    closeLeft = panelLeft + panelWidth - app.measureCloseSize - 6
    closeTop = panelTop + 6
    closeRight = closeLeft + app.measureCloseSize
    closeBottom = closeTop + app.measureCloseSize
    
    # click "X" to exit measure mode
    if app.measureMode and (closeLeft <= mX <= closeRight and closeTop <= mY <= closeBottom):
        hadSegments = len(app.measureSegments) > 0
        app.measureMode = False
        app.measureStart = None
        app.measureTempEnd = None
        app.measureSegments = []
        app.lastMeasureHintSegmentIndex = None
        app.showMeasureEscHint = False
        if hadSegments:
            registerAction(app)
        return None
        
    # click the panel to turn measure mode ON
    if (panelLeft <= mX <= panelLeft + panelWidth and
        panelTop <= mY <= panelTop + panelHeight and not app.measureMode):
        app.measureMode = True
        app.measureStart = None
        app.measureTempEnd = None
        app.measureSegments = []
        return None
        
    # measure mode click-click logic
    if app.measureMode:
        if isInsideRect(mX, mY, app.room.roomLeft, app.room.roomTop,
                        app.room.roomWidth, app.room.roomHeight):
            # if no current start point, start a new segment
            if app.measureStart == None:
                app.measureStart = (mX, mY)
                app.measureTempEnd = (mX, mY)
            else: # we already have start point, so this click finalizes segment
                startX, startY = app.measureStart
                endX, endY = mX, mY
                app.measureSegments.append(((startX, startY), (endX, endY)))
                
                app.lastMeasureHintSegmentIndex = len(app.measureSegments) - 1
                app.showMeasureEscHint = True
                
                # full valid line so register
                registerAction(app)
                
                # clears current ruler so next click starts fresh
                app.measureStart = None
                app.measureTempEnd = None
         
        # ignore clicks outside room while in measure mode       
        return None
        
    # normal behavior when not in measure mode    
    app.lastMouseX = mX
    app.lastMouseY = mY
    app.didDrag = False
    selectedItem = paletteCheck(app, mX, mY)
    if selectedItem != None:
        spawnFurniture(app, selectedItem, mX, mY)
        return None
    app.room.handleMousePress(mX, mY)
    
def design_onMouseDrag(app, mX, mY):
    app.lastMouseX = mX
    app.lastMouseY = mY
    
    # dragging does nothing in measure mode
    if app.measureMode:
        return None
        
    app.room.handleMouseDrag(mX, mY)
    furniture = app.room.selectedFurniture
    if furniture != None:
        app.didDrag = True
        app.ghostIsValid = isValidPlacement(app, furniture)
        
def design_onMouseRelease(app, mX, mY):
    furniture = app.room.selectedFurniture
    if furniture != None and furnitureOverTrash(app, furniture):
        # delete furniture (valid move)
        app.room.furnitureList.remove(furniture)
        app.room.selectedFurniture = None
        
        registerAction(app)
        
        app.ghostIsValid = True
        app.lastMouseX = None
        app.lastMouseY = None
        return None
        
    if furniture != None and not app.ghostIsValid:
        # if from palette spawn, remove if invalid position
        if app.room.dragFromPalette:
            app.room.furnitureList.remove(furniture)
            app.room.selectedFurniture = None
        # if picking up existing furniture, revert back to original position
        else:
            furniture.left = app.room.originalLeft
            furniture.top = app.room.originalTop
            if app.room.originalAngle != None:
                furniture.angle = app.room.originalAngle
            if app.room.originalWidth != None:
                furniture.width = app.room.originalWidth
            if app.room.originalHeight != None:
                furniture.height = app.room.originalHeight
     
    elif furniture != None and app.room.dragFromPalette and not app.didDrag:
        app.room.furnitureList.remove(furniture)
        app.room.selectedFurniture = None
    
    elif furniture != None and app.ghostIsValid and app.didDrag:
        # valid placement so register
        registerAction(app)

    app.ghostIsValid = True
    app.lastMouseX = None
    app.lastMouseY = None
    app.didDrag = False
    
def design_onMouseMove(app, mX, mY):
    app.mouseX = mX
    app.mouseY = mY
    
    app.hoverDoor = False
    app.hoverWindowIndex = None
    
    if app.room.doorRect != None:
        doorX, doorY, doorWidth, doorHeight = app.room.doorRect
        if isInsideRect(mX, mY, doorX, doorY, doorWidth, doorHeight):
            app.hoverDoor = True
            return None
            
    for i, (wx, wy, ww, wh) in enumerate(app.room.windowRects):
        if isInsideRect(mX, mY, wx, wy, ww, wh):
            app.hoverWindowIndex = i
            return None
    
    if app.measureMode and app.measureStart != None:
        # only show preview inside room
        app.measureTempEnd = (mX, mY)
    
def design_onKeyPress(app, key):
    if key == 'R' or key == 'r':
        furniture = app.room.selectedFurniture
        if furniture != None:
            rotateSelectedFurniture(app, furniture)
    elif key == 'z':
        undoAction(app)
    elif key == 'y':
        redoAction(app)
    elif key == 'escape' and app.measureMode:
        hadSegments = len(app.measureSegments) > 0
        app.measureMode = False
        app.measureStart = None
        app.measureTempEnd = None
        app.measureSegments = []
        app.lastMeasureHintSegmentIndex = None
        app.showMeasureEscHint = False
        if hadSegments:
            registerAction(app)
        
def design_redrawAll(app):
    drawPalette(app)
    drawTrash(app)
    app.room.draw()
    drawRoomDimensions(app)
    drawGhost(app)
    drawFurnitureTooltip(app)
    
    drawMeasurePanel(app)
    drawMeasureRuler(app)
    
    canUndo = len(app.history) > 1
    canRedo = len(app.redoStack) > 0
    
    isBackHovering = (app.mouseX != None and isInsideRect(app.mouseX, app.mouseY,
                        app.backButtonLeft, app.backButtonTop, app.layoutButtonWidth,
                        app.layoutButtonHeight))
                        
    isUndoHovering = (canUndo and app.mouseX != None and isInsideRect(app.mouseX, app.mouseY,
                        app.undoButtonLeft, app.undoButtonTop, app.undoButtonSize,
                        app.undoButtonSize))
                        
    isRedoHovering = (canRedo and app.mouseX != None and isInsideRect(app.mouseX, app.mouseY,
                        app.redoButtonLeft, app.redoButtonTop, app.redoButtonSize,
                        app.redoButtonSize))
    
    # back to layouts button
    drawRect(app.backButtonLeft, app.backButtonTop, app.backButtonWidth,
             app.backButtonHeight, fill = 'darkSlateBlue', 
             border = 'gold' if isBackHovering else 'black',
             borderWidth = 4 if isBackHovering else 2)
    drawLabel('Back to Layouts', app.backButtonLeft + app.backButtonWidth / 2,
              app.backButtonTop + app.backButtonHeight / 2,
              size = 20, bold = True, fill = 'white', font = 'monospace')
    
    # undo / redo buttons
    undoFill = 'darkSlateBlue' if canUndo else 'lightGray'
    undoOpacity = 100 if canUndo else 20
    undoBorderColor = 'gold' if isUndoHovering else 'black'
    undoBorderWidth = 4 if isUndoHovering else 2
    undoArrowColor = 'white' if canUndo else 'gainsboro'
    
    drawRect(app.undoButtonLeft, app.undoButtonTop, app.undoButtonSize,
             app.undoButtonSize, fill = undoFill, 
             border = undoBorderColor, borderWidth = undoBorderWidth,
             opacity = undoOpacity)
             
    undoCx = app.undoButtonLeft + app.undoButtonSize / 2
    undoCy = app.undoButtonTop + app.undoButtonSize / 2
    
    drawLabel('Z', app.undoButtonLeft + 8, app.undoButtonTop + app.undoButtonSize - 10, size = 15,
              font = 'monospace', bold = True, fill = undoArrowColor)
             
    drawLine(undoCx + 8, undoCy, undoCx - 8, undoCy,
             lineWidth = 4, fill = undoArrowColor, arrowStart = False, arrowEnd = True)
    
    redoFill = 'darkSlateBlue' if canRedo else 'lightGray'
    redoOpacity = 100 if canRedo else 20
    redoBorderColor = 'gold' if isRedoHovering else 'black'
    redoBorderWidth = 4 if isRedoHovering else 2
    redoArrowColor = 'white' if canRedo else 'gainsboro'
             
    drawRect(app.redoButtonLeft, app.redoButtonTop, app.redoButtonSize,
             app.redoButtonSize, fill = redoFill, 
             border = redoBorderColor, borderWidth = redoBorderWidth, 
             opacity = redoOpacity)
    
    redoCx = app.redoButtonLeft + app.redoButtonSize / 2
    redoCy = app.redoButtonTop + app.redoButtonSize / 2
    
    drawLabel('Y', app.redoButtonLeft + 8, app.redoButtonTop + app.redoButtonSize - 10, size = 15,
              font = 'monospace', bold = True, fill = redoArrowColor)
    
    drawLine(redoCx - 8, redoCy, redoCx + 8, redoCy,
             lineWidth = 4, fill = redoArrowColor, arrowStart = False, arrowEnd = True)
    
##########################################
# PALETTE LOGIC
##########################################
    
def drawPalette(app):
    headerHeight = 40
    headerGap = 10
    headerTop = app.paletteTop - headerHeight - headerGap
    headerLeft = app.paletteLeft
    
    drawRect(headerLeft, headerTop, app.paletteWidth, headerHeight,
             fill = 'gray', border = 'black')
    drawLabel('Furniture Items', headerLeft + app.paletteWidth / 2,
              headerTop + headerHeight / 2, size = 14, bold = True, font = 'monospace', fill = 'white')
    for i, item in enumerate(app.paletteItems): # index and key
        left = app.paletteLeft
        top = app.paletteTop + i * app.paletteSpacing
        cX = app.paletteLeft + app.paletteWidth / 2
        cY = top + app.paletteHeight / 2
        
        isHovering = (app.mouseX != None and isInsideRect(app.mouseX, app.mouseY,
                      left, top, app.paletteWidth, app.paletteHeight))
                      
        baseFill = rgb(253, 248, 238)
        glowFill = rgb(255, 245, 200)
        fillColor = glowFill if isHovering else baseFill
        
        drawRect(left, top, app.paletteWidth, app.paletteHeight, fill = fillColor, border = 'black')
        
        labelText = item['kind'].upper()
        labelY = top + 18
        drawLabel(labelText, cX, labelY, size = 14, font = 'monospace', bold = True)
        
        maxWidth = app.paletteWidth - 40
        maxHeight = app.paletteHeight - 60
        scale = min(maxWidth / item['width'], maxHeight / item['height'])
        drawImage(item['image'], cX, cY, width = item['width'] * scale, height = item['height'] * scale, align = 'center')
        
def paletteCheck(app, mX, mY):
    for i, item in enumerate(app.paletteItems):
        left = app.paletteLeft
        top = app.paletteTop + i * app.paletteSpacing
        right = left + app.paletteWidth
        bottom = top + app.paletteHeight
        if left <= mX <= right and top <= mY <= bottom:
            return item
    return None
    
def spawnFurniture(app, paletteItem, mX, mY):
    width = paletteItem['width']
    height = paletteItem['height']
    newLeft = mX - width / 2
    newTop = mY - height / 2
    newFurniture = Furniture(
        paletteItem['kind'],
        newLeft,
        newTop,
        width,
        height,
        image = paletteItem['image'],
        angle = 0
    )
    app.room.addFurniture(newFurniture)
    app.room.selectedFurniture = newFurniture
    app.room.dragOffsetX = mX - newFurniture.left
    app.room.dragOffsetY = mY - newFurniture.top
    
    app.room.dragFromPalette = True
    
##########################################
# TRASH LOGIC
##########################################

def drawTrash(app):
    drawImage(app.trashImage, app.trashLeft, app.trashTop, width = app.trashSize, height = app.trashSize)
    
def furnitureOverTrash(app, furniture): # rectangles overlap
    furnitureRight = furniture.left + furniture.width
    trashRight = app.trashLeft + app.trashSize
    furnitureBottom = furniture.top + furniture.height
    trashBottom = app.trashTop + app.trashSize
    return (furniture.left <= trashRight 
            and furnitureRight >= app.trashLeft
            and furniture.top <= trashBottom
            and furnitureBottom >= app.trashTop)
            
##########################################
# GHOST LOGIC
##########################################

def drawGhost(app):
    furniture = app.room.selectedFurniture
    if furniture == None:
        return None
    color = 'green' if app.ghostIsValid else 'red'
    drawRect(furniture.left, furniture.top, furniture.width, furniture.height, fill = None, border = color, borderWidth = 4)

def isValidPlacement(app, furniture):
    # check if furniture is in room
    furnitureRight = furniture.left + furniture.width
    furnitureBottom = furniture.top + furniture.height
    roomRight = app.room.roomLeft + app.room.roomWidth
    roomBottom = app.room.roomTop + app.room.roomHeight
    insideRoom = (furniture.left >= app.room.roomLeft 
            and furnitureRight <= roomRight
            and furniture.top >= app.room.roomTop
            and furnitureBottom <= roomBottom)
            
    if not insideRoom:
        return False
        
        # check if furniture overlaps with another furniture
        
    for otherFurniture in app.room.furnitureList:
        if otherFurniture != furniture:
            otherFurnitureRight = otherFurniture.left + otherFurniture.width
            otherFurnitureBottom = otherFurniture.top + otherFurniture.height
            
            doesOverlap = (furniture.left <= otherFurnitureRight
                           and furnitureRight >= otherFurniture.left
                           and furniture.top <= otherFurnitureBottom
                           and furnitureBottom >= otherFurniture.top)
                           
            if doesOverlap:
                return False
    return True
    
def rotateSelectedFurniture(app, furniture):
    # save old state so we can revert if invalid
    oldAngle = furniture.angle
    oldLeft = furniture.left
    oldTop = furniture.top
    oldWidth = furniture.width
    oldHeight = furniture.height
    
    # below is the same as tetris rotation logic
    furnitureCenterX = oldLeft + oldWidth / 2
    furnitureCenterY = oldTop + oldHeight / 2
    
    newAngle = (oldAngle + 90) % 360
    
    newWidth = oldHeight
    newHeight = oldWidth
    
    newLeft = furnitureCenterX - newWidth / 2
    newTop = furnitureCenterY - newHeight / 2
    
    furniture.angle = newAngle
    furniture.width = newWidth
    furniture.height = newHeight
    furniture.left = newLeft
    furniture.top = newTop
    
    if not isValidPlacement(app, furniture):
        # revert everything if invalid
        furniture.angle = oldAngle
        furniture.left = oldLeft
        furniture.top = oldTop
        furniture.width = oldWidth
        furniture.height = oldHeight
        app.ghostIsValid = False
    else:
        app.ghostIsValid = True
        # this is so dragging stays smooth after rotation
        if app.lastMouseX != None and app.lastMouseY != None:
            app.room.dragOffsetX = app.lastMouseX - furniture.left
            app.room.dragOffsetY = app.lastMouseY - furniture.top
         
        # rotation was valid so register
        registerAction(app) 
            
def drawFurnitureTooltip(app):
    if app.mouseX == None or app.mouseY == None:
        return None
    hoveredFurniture = app.room.getFurnitureAt(app.mouseX, app.mouseY)
    if hoveredFurniture != None:
        hoveredFurniture.drawTooltip(app)
        return None
    
    # door tooltip
    if app.hoverDoor and app.room.doorRect != None:
        doorX, doorY, doorWidth, doorHeight = app.room.doorRect
        drawSimpleTooltip(doorX + doorWidth / 2, doorY, 'DOOR')
        
    # window tooltip
    if app.hoverWindowIndex != None:
        windowX, windowY, windowWidth, windowHeight = app.room.windowRects[app.hoverWindowIndex]
        drawSimpleTooltip(windowX + windowWidth / 2, windowY, 'WINDOW')
        return None
        
def drawSimpleTooltip(centerX, topY, message):
    fontSize = 12
    paddingX = 6
    paddingY = 3
    
    approxTextWidth = len(message) * fontSize * 0.6
    boxWidth = approxTextWidth + 2 * paddingX
    boxHeight = fontSize + 2 * paddingY
    
    gap = 4
    bottomY = topY - gap
    top = bottomY - boxHeight
    left = centerX - boxWidth / 2
    labelY = top + paddingY + fontSize / 2
    
    drawRect(left, top, boxWidth, boxHeight, fill = 'black', opacity = 80)
    drawLabel(message, centerX, labelY, size = fontSize, font = 'monospace', bold = True, fill = 'white')
    
##########################################
# RULER
##########################################
 
def drawMeasurePanel(app):
    left = app.measurePanelLeft
    top = app.measurePanelTop
    width = app.measurePanelWidth
    height = app.measurePanelHeight
    
    isHovering = app.mouseX != None and isInsideRect(app.mouseX, app.mouseY, left, top, width, height)
    
    baseFill = rgb(255, 252, 246)
    glowFill = rgb(255, 245, 200)
    
    if app.measureMode:
        borderColor = 'green'
        borderWidth = 4
    else:
        borderColor = 'black'
        borderWidth = 2
        
    fillColor = glowFill if isHovering else baseFill
    
    drawRect(left, top, width, height, fill = fillColor, border = borderColor, borderWidth = borderWidth)
    
    # draw ruler icon
    centerX = left + width / 2
    centerY = top + height / 2
    drawImage(app.rulerImage, centerX, centerY, width = width * 0.5, height = height * 0.5, align = 'center')
    
    drawLabel('RULER', left + width / 2, top + 24, size = 14, font = 'monospace', bold = True)
    
    if isHovering:
        message = "MEASUREMENT MODE"
        fontSize = 12
        paddingX = 8
        paddingY = 4
        approxTextWidth = len(message) * fontSize * 0.6
        boxWidth = approxTextWidth + 2 * paddingX
        boxHeight = fontSize + 2 * paddingY
        
        tooltipCenterX = centerX
        gap = 6
        bottomY = top - gap
        tooltipLeft = tooltipCenterX - boxWidth / 2
        tooltipTop = bottomY - boxHeight
        
        labelY = tooltipTop + paddingY + fontSize / 2
        
        drawRect(tooltipLeft, tooltipTop, boxWidth, boxHeight, fill = 'black', opacity = 80)
        drawLabel(message, tooltipCenterX, labelY, size = fontSize, font = 'monospace', bold = True, fill = 'white')
        
    # X button only when active
    if app.measureMode:
        closeSize = app.measureCloseSize
        closeLeft = left + width - closeSize - 6
        closeTop = top + 6
        isCloseHovering = app.mouseX != None and isInsideRect(app.mouseX, app.mouseY, closeLeft, closeTop, closeSize, closeSize)
        closeBorderColor = 'gold' if isCloseHovering else 'black'
        drawRect(closeLeft, closeTop, closeSize, closeSize, fill = 'firebrick', border = closeBorderColor)
        drawLabel('X', closeLeft + closeSize / 2, closeTop + closeSize / 2,
                  size = 10, bold = True, fill = 'white')

def drawMeasureRuler(app):
    # not in measurement mode, so don't draw ruler
    if not app.measureMode:
        return None
    
    # get pixel to inches scale factors for current layout
    scaleX, scaleY = getCurrentScaleFactors(app)
    # not in design screen / measurement mode, so don't scale 
    if scaleX == None or scaleY == None:
        return None
     
    # draw all saved line segments  
    for i, (start, end) in enumerate(app.measureSegments):
        startX, startY = start
        endX, endY = end
        
        drawLine(startX, startY, endX, endY, lineWidth = 3, fill = 'darkGreen')
        
        # distance in PIXELS
        dxPixels = endX - startX
        dyPixels = endY - startY
        
        # convert to distance in INCHES (real-world)
        dxInches = dxPixels * scaleX
        dyInches = dyPixels * scaleY
        distInches = (dxInches ** 2 + dyInches ** 2) ** 0.5
        
        # string representation of distance
        label = formatDistanceInches(distInches)
        
        midX = (startX + endX) / 2
        midY = (startY + endY) / 2 - 12
        drawLabel(label, midX, midY, size = 14, font = 'monospace', bold = True, fill = 'darkGreen')
        
        # tooltip logic
        if app.showMeasureEscHint and app.lastMeasureHintSegmentIndex == i:
            message = "PRESS 'esc' TO RETURN TO LAYOUT MODE"
            fontSize = 12
            paddingX = 8
            paddingY = 4
            
            approxTextWidth = len(message) * fontSize * 0.6
            boxWidth = approxTextWidth + 2 * paddingX
            boxHeight = fontSize + 2 * paddingY
            
            gap = 6
            bottomY = midY - gap
            top = bottomY - boxHeight
            left = midX - boxWidth / 2
            labelY = top + paddingY + fontSize / 2
            
            drawRect(left, top, boxWidth, boxHeight, fill = 'black', opacity = 50)
            drawLabel(message, midX, labelY, size = fontSize, font = 'monospace', bold = True, fill = 'white')
        
    # draw current preview segment
    if app.measureStart != None and app.measureTempEnd != None:
        startX, startY = app.measureStart
        endX, endY = app.measureTempEnd
        
        drawLine(startX, startY, endX, endY, lineWidth = 2, fill = 'darkOliveGreen')
        
        # distance in PIXELS
        dxPixels = endX - startX
        dyPixels = endY - startY
        
        # convert to distance in INCHES
        dxInches = dxPixels * scaleX
        dyInches = dyPixels * scaleY
        distInches = (dxInches ** 2 + dyInches ** 2) ** 0.5
        
        # string representation of distance
        label = formatDistanceInches(distInches)
        
        midX = (startX + endX) / 2
        midY = (startY + endY) / 2 - 12
        drawLabel(label, midX, midY, size = 12, font = 'monospace', bold = True, fill = 'darkOliveGreen')
        
def getCurrentScaleFactors(app):
    if app.currentLayout == 'single':
        widthInches = 12 * 12 + 11
        heightInches = 8 * 12 + 7
        return widthInches / app.singleRoomWidth, heightInches / app.singleRoomHeight
        
    elif app.currentLayout == 'double':
        widthInches = 11 * 12 + 11
        heightInches = 14 * 12 + 3
        return widthInches / app.doubleRoomWidth, heightInches / app.doubleRoomHeight
      
    elif app.currentLayout == 'triple':
        widthInches = 24 * 12 + 10
        heightInches = 12 * 12 + 9
        return widthInches / app.tripleRoomWidth, heightInches / app.tripleRoomHeight  
    else:
        return (None, None)
    
def formatDistanceInches(inches):
    total = rounded(inches)
    feet = total // 12
    inches = total % 12 # remainder, inches remaining
    return f"{feet}' {inches}\""
    
##########################################
# DIMENSION LINES
##########################################

def drawRoomDimensions(app):
    if app.room.roomWidth == 0 or app.room.roomHeight == 0:
        return None
        
    roomLeft = app.room.roomLeft
    roomTop = app.room.roomTop
    roomWidth = app.room.roomWidth
    roomHeight = app.room.roomHeight
    
    if app.currentLayout == 'single':
        widthLabel = app.singleWidthLabel
        heightLabel = app.singleHeightLabel
    elif app.currentLayout == 'double':
        widthLabel = app.doubleWidthLabel
        heightLabel = app.doubleHeightLabel
    elif app.currentLayout == 'triple':
        widthLabel = app.tripleWidthLabel
        heightLabel = app.tripleHeightLabel
    else:
        return None
        
    horizontalY = roomTop - 25
    drawLine(roomLeft, horizontalY, roomLeft + roomWidth, horizontalY, lineWidth = 2, arrowStart = True, arrowEnd = True)
    drawLabel(widthLabel, roomLeft + roomWidth / 2, horizontalY - 10, size = 14, font = 'monospace', bold = True)
     
    verticalX = roomLeft - 25
    drawLine(verticalX, roomTop, verticalX, roomTop + roomHeight, lineWidth = 2, arrowStart = True, arrowEnd = True)
    drawLabel(heightLabel, verticalX - 10, roomTop + roomHeight / 2, size = 14, font = 'monospace', bold = True, rotateAngle = 270)
        
##########################################
# POINT-IN-RECT HELPER
##########################################
 
def isInsideRect(mX, mY, left, top, width, height):
    right, bottom = left + width, top + height
    return left <= mX <= right and top <= mY <= bottom
    
################################################
# CLASSES
################################################

class Furniture:
    def __init__(self, kind, left, top, width, height, image, angle):
        self.kind = kind
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.image = image
        self.angle = angle
        
        # image draw size to maintain nice proportions
        self.drawWidth = width
        self.drawHeight = height
        
    def containsPoint(self, x, y):
        right = self.left + self.width
        bottom = self.top + self.height
        return (self.left <= x <= right) and (self.top <= y <= bottom)
        
    def furnitureDraw(self):
        furnitureCenterX = self.left + self.width / 2
        furnitureCenterY = self.top + self.height / 2
        drawImage(self.image, furnitureCenterX, furnitureCenterY, 
                  width = self.drawWidth, height = self.drawHeight, 
                  align = 'center', rotateAngle = self.angle)
                  
    def drawTooltip(self, app):
        if not app.measureMode:
            message = "CLICK ITEM, THEN PRESS 'r' TO ROTATE"
            fontSize = 12
            paddingX = 8
            paddingY = 4
            
            approxTextWidth = len(message) * fontSize * 0.6
            boxWidth = max(approxTextWidth + 2 * paddingX, 220)
            boxHeight = fontSize + 2 * paddingY
            
            centerX = self.left + self.width / 2
            gap = 6
            bottomY = self.top - gap
            left = centerX - boxWidth / 2
            top = bottomY - boxHeight
            
            labelY = top + paddingY + fontSize / 2
            drawRect(left, top, boxWidth, boxHeight, fill = 'black', opacity = 80)
            drawLabel(message, centerX, labelY, size = fontSize, font = 'monospace', bold = True, fill = 'white')
        
class Room:
    def __init__(self, roomLeft, roomTop, roomWidth, roomHeight, doorRect, windowRects):
        self.roomLeft = roomLeft
        self.roomTop = roomTop
        self.roomWidth = roomWidth
        self.roomHeight = roomHeight
        self.doorRect = doorRect
        self.windowRects = windowRects
        self.furnitureList = []
        self.selectedFurniture = None
        
        # furniture object can drag normally no matter the location pressed
        self.dragOffsetX = 0 # furniture's cx doesn't "snap" right/left suddenly
        self.dragOffsetY = 0 # furniture's cy doesn't "snap" up/down suddenly
        
        # snap-back behavior
        self.originalLeft = None
        self.originalTop = None
        self.dragFromPalette = False
        
        # snap-back behavior to remember original orientation and dimensions
        self.originalAngle = None
        self.originalWidth = None
        self.originalHeight = None
        
    def addFurniture(self, furniture):
        self.furnitureList.append(furniture)
        
    def getFurnitureAt(self, mX, mY):
        for furniture in reversed(self.furnitureList): # if furniture pieces overlap, returns topmost
            if furniture.containsPoint(mX, mY):
                return furniture
        return None
    
    # functions BELOW are called by event handlers 
    
    def handleMousePress(self, mX, mY):
        furniture = self.getFurnitureAt(mX, mY)
        if furniture != None:
            self.selectedFurniture = furniture
            self.dragOffsetX = mX - furniture.left
            self.dragOffsetY = mY - furniture.top
            
            # drag started from the room, no the palette
            self.dragFromPalette = False
            
            # remember original position for possible snap-back
            self.originalLeft = furniture.left
            self.originalTop = furniture.top
            self.originalAngle = furniture.angle
            self.originalWidth = furniture.width
            self.originalHeight = furniture.height
        else:
            self.selectedFurniture = None
        
    def handleMouseDrag(self, mX, mY):
        if self.selectedFurniture != None:
            self.selectedFurniture.left = mX - self.dragOffsetX
            self.selectedFurniture.top = mY - self.dragOffsetY
            
    def draw(self):
        # draw the room
        drawRect(self.roomLeft, self.roomTop, self.roomWidth, self.roomHeight, fill = None, border = 'black')
        
        # draw the door
        (doorX, doorY, doorW, doorH) = self.doorRect
        drawRect(doorX, doorY, doorW, doorH, fill = 'red')
        
        # draw all the windows
        for (windowX, windowY, windowW, windowH) in self.windowRects:
            drawRect(windowX, windowY, windowW, windowH, fill = 'lightBlue')
           
        # draw all the furniture
        for furniture in self.furnitureList:
            furniture.furnitureDraw()

################################################
# HISTORY / SNAPSHOTS FOR UNDO AND REDO
################################################

def snapshotRoom(app):
    # capture current state
    furnitureData = []
    for furniture in app.room.furnitureList:
        furnitureData.append({
            'kind' : furniture.kind,
            'left' : furniture.left,
            'top' : furniture.top,
            'width' : furniture.width,
            'height' : furniture.height,
            'angle' : furniture.angle,
            'image' : furniture.image,
            'drawWidth' : furniture.drawWidth,
            'drawHeight' : furniture.drawHeight
        })
    return {
        'furniture' : furnitureData,
        'measureSegments' : copy.copy(app.measureSegments), # prevent aliasing
        'measureMode' : app.measureMode,
        'lastMeasureHintSegmentIndex' : app.lastMeasureHintSegmentIndex,
        'showMeasureEscHint' : app.showMeasureEscHint
    }
    
def applySnapshot(app, snapshot):
    # restore a snapshot into the current app
    app.room.furnitureList = []
    for data in snapshot['furniture']:
        # add every piece of furniture back
        furniture = Furniture(
                    data['kind'],
                    data['left'],
                    data['top'],
                    data['width'],
                    data['height'],
                    data['image'],
                    data['angle'],
                    )
        
        # restore original drawing size so scaling is consistent 
        furniture.drawWidth = data['drawWidth']
        furniture.drawHeight = data['drawHeight']
        
        app.room.addFurniture(furniture)
    # add line segments back
    app.measureSegments = copy.copy(snapshot['measureSegments']) # prevent aliasing
    app.measureMode = snapshot['measureMode']
    app.lastMeasureHintSegmentIndex = snapshot['lastMeasureHintSegmentIndex']
    app.showMeasureEscHint = snapshot['showMeasureEscHint']
    
    # always clear any in-progress measurement preview
    app.measureStart = None
    app.measureTempEnd = None
    
    # clear states
    app.room.selectedFurniture = None
    app.ghostIsValid = True
    app.lastMouseX = None # nothing is being hovered over after undo/redo
    app.lastMouseY = None 
    
def registerAction(app):
    # this works only after a VALID move completes
    snapshot = snapshotRoom(app)
    app.history.append(snapshot)
    app.redoStack = []
    
def undoAction(app):
    if len(app.history) <= 1:
        return None
    last = app.history.pop()
    app.redoStack.append(last)
    applySnapshot(app, app.history[-1])
    
def redoAction(app):
    if len(app.redoStack) == 0:
        return None
    snapshot = app.redoStack.pop()
    app.history.append(snapshot)
    applySnapshot(app, snapshot)
    
def main():
    runAppWithScreens(initialScreen = 'home', width = 1280, height = 720)
    
main()
