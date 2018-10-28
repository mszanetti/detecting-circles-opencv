# LICENSE: GPL V 3.0
# by MARCELO SERRANO ZANETTI - 28.October.2018
  
# LIBRARIES
import numpy as np
import cv2
import math
import random as rand
import sys
rand.seed(None)
  
# PARAMETERS 
infile = 'match_original.mp4'
bground= 'color'
outfile= 'output_%s.avi'%bground
width  = 1920
height = 1080
tol    = 90
rep    = 10
green  = (0,255,0)
blue   = (255,0,0)
red    = (0,0,255)
white  = (255,255,255)

# CHECK COLLISION BETWEEN CIRCLES
def circlescollide(i,j):
    dx = int(j[0])-int(i[0])
    dy = int(j[1])-int(i[1])
    r1 = int(j[2])
    r2 = int(i[2])
    d  = math.sqrt((dx*dx)+(dy*dy))
    if d<=(r1+r2):
        return True
    else:
        return False

# AVERAGE PIXELS WITHIN A CIRCLE
# MARK CIRCLES THAT ARE BELOW
# THRESHOLD VALUE: DARK CIRCLES!
def avcircle(x,y,r,tol,rep,frame,width,height):
    c0 = 0.0
    c1 = 0.0
    c2 = 0.0
    n  = 0.0  
    for i in range(0,rep):
        px=rand.randint(x-r,x+r)
        py=rand.randint(y-r,y+r)
        if px>=width:
            px=width
        if py>=height:
            py=height
        if px<1:
            px=1
        if py<1:
            py=1
        if (px-x)**2+(py-y)**2<=(r*r):
            n  += 1.0  
            c0 += float(frame[py-1,px-1,0])
            c1 += float(frame[py-1,px-1,1])
            c2 += float(frame[py-1,px-1,2])
    if n>0 and c0/n<=tol and c1/n<=tol and c2/n<=tol:
        return True
    else:
        return False
  
# INPUT AND OUTPUT FILES  
cap         = cv2.VideoCapture(infile)
fourcc      = cv2.VideoWriter_fourcc(*'XVID')
out         = cv2.VideoWriter(outfile,fourcc, 30.0, (width,height))
# FRAME COUNTER : PROGRESS 
property_id = int(cv2.CAP_PROP_FRAME_COUNT) 
frames      = int(cv2.VideoCapture.get(cap, property_id))
frameCounter= 0   

# MAIN LOOP
while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        frameCounter += 1
        gray          = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frameg        = cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
         
        # DETECT CIRCLES
        circles = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,1,20, param1=50,param2=30,minRadius=10,maxRadius=100)
       	if not circles.any():
            print "NoneType"
            break
        # CONVERT PIXEL COORDINATES TO INT
        circles = np.uint32(np.around(circles))

        # PROGRESS LIST
        l    = []
        done = {}

        # CHECK IT CIRCLE TO AVOID OVERLAP BETWEEN TWO OR MORE CIRCLES
        for i in circles[0,:]:
          li=str(i)
          # ONLY CONSIDER DARK CIRCLES
          if not avcircle(int(i[0]),int(i[1]), int(i[2]), tol, rep, frameg, width, height):
              done[li]=1
              continue
          else:
            if li not in done:
                inter=[] 
                inter.append(( int(i[0]),int(i[1]),int(i[2]) ))
                done[li]=1
                for j in circles[0,:]:
                    lj=str(j)
                    # ONLY CONSIDER DARK CIRCLES
                    if avcircle(int(j[0]),int(j[1]),int(j[2]), tol, rep, frameg, width, height):
                        if lj not in done:
                            # MARK COLLISIONS
                            if circlescollide(i,j):   
                                inter.append(( int(j[0]),int(j[1]),int(j[2]) ))
                                done[lj]=1
                    else:
                        done[lj]=1

                # AVERAGE COLLISIONS
                mx = 0
                my = 0 
                mr = 0
                n  = len(inter)
                for j in inter:
                    mx+=j[0]
                    my+=j[1]
                    mr+=j[2]
                mx/=n
                my/=n  
                mr/=n
                # CONSIDER THE AVERAGE CIRCLE ONLY
                l.append(( int(mx),int(my),int(mr)))

        # DRAW DETECTED CIRCLES
        if bground=='color':
            finalFrame=frame
        elif bground=='gray':
            finalFrame=frameg
        for i in l: 
	    cv2.circle(finalFrame,(i[0],i[1]),i[2],green,5)
            for j in l:          
                cv2.line(finalFrame,(i[0],i[1]),(j[0],j[1]),blue,1)
                 
        # MONITOR PROGRESS  
        progress = (100*frameCounter/float(frames))

        # ANIMATING TEXT
        if progress >=40:
            text       = "MATCH"
            font       = cv2.FONT_HERSHEY_SIMPLEX
            fontScale  = 5
            fontColor  = green
            lineType   = 4
            thickness  = 15
            size       = cv2.getTextSize(text, font, fontScale, thickness)
            position   = (int((width-size[0][0])/2),int((height-size[0][1])))
            if progress%10<5:
			cv2.putText(finalFrame,text,position,font,fontScale,fontColor,thickness,lineType)                        

        sys.stdout.write("\r PROGRESS: %.2f %%"%progress)
        sys.stdout.flush()

        # WRITE FRAME TO OUTPUT FILE
	out.write(finalFrame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else: 
        break    
   
# CLEANING UP
cap.release()
out.release()
cv2.destroyAllWindows()
