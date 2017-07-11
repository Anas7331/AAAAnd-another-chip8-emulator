import pygame, sys, time
from random import randint
from pygame.locals import *
pygame.init()
BEEP_SOUND_FILE = 'beep.wav'
pygame.mixer.init(44100)
sound = pygame.mixer.Sound(BEEP_SOUND_FILE)
A = open('INVADERS','rb')
Memory = [0] * 4096
i = 0x200
freq = 1/(99999)
fonts = [0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
         0x20, 0x60, 0x20, 0x20, 0x70, # 1
         0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
         0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
         0x90, 0x90, 0xF0, 0x10, 0x10, # 4
         0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
         0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
         0xF0, 0x10, 0x20, 0x40, 0x40, # 7
         0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
         0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
         0xF0, 0x90, 0xF0, 0x90, 0x90, # A
         0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
         0xF0, 0x80, 0x80, 0x80, 0xF0, # C
         0xE0, 0x90, 0x90, 0x90, 0xE0, # D
         0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
         0xF0, 0x80, 0xF0, 0x80, 0x80  # F
         ]
for x in range(80):
    Memory[x] = fonts[x]
for b in A.read():
    Memory[i] = b
    i += 1
I = 0
gfx = [0] * 64*32
PC = 0x200
Vi = [0] * 16
key_inputs = [0]*16
Stack = []
sound_timer = 0
delay_timer = 0
Pixelsize = 10
DISPLAYSURF = pygame.display.set_mode((64 * Pixelsize, 32 * Pixelsize))
pygame.display.set_caption('Chyp8')
Timersfreq = 60
t = 0
T = 0
def emulateCPU():
    global PC, Memory, Stack, I, gfx, delay_timer, sound_timer
    opcode =  (Memory[PC] << 8) + Memory[PC + 1]
    if opcode == 0x00E0:
        gfx = [0] * 64*32
        PC += 2
    if opcode == 0x00EE:
        PC = Stack.pop()
        PC += 2
    if (opcode & 0xF000) == 0x1000:
        PC = opcode & 0x0FFF
    if (opcode & 0xF000) == 0x2000:
        Stack.append(PC)
        PC = opcode & 0x0FFF
    if (opcode & 0xF000) == 0x3000:
        if Vi[(opcode & 0x0F00) >> 8] == (opcode & 0x00FF):
            PC += 4
        else:
            PC += 2
    if (opcode & 0xF000) == 0x4000:
        if Vi[(opcode & 0x0F00) >> 8] != (opcode & 0x00FF):
            PC += 4
        else:
            PC += 2
    if (opcode & 0xF000) == 0x5000:
        if Vi[(opcode & 0x0F00) >> 8] == Vi[(opcode & 0x00F0) >> 4]:
            PC += 4
        else:
            PC += 2
    if (opcode & 0xF000) == 0x6000:
        Vi[(opcode & 0x0F00) >> 8] = (opcode & 0x00FF)
        PC += 2
    if (opcode & 0xF000) == 0x7000:
        Vi[(opcode & 0x0F00) >> 8] += (opcode & 0x00FF)
        Vi[(opcode & 0x0F00) >> 8] &= 0xff
        PC += 2
    if (opcode & 0xF00F) == 0x8000:
        Vi[(opcode & 0x0F00) >> 8] = Vi[(opcode & 0x00F0) >> 4]
        PC +=2
    if (opcode & 0xF00F) == 0x8001:
        Vi[(opcode & 0x0F00) >> 8] |= Vi[(opcode & 0x00F0) >> 4]
        PC += 2
    if (opcode & 0xF00F) == 0x8002:
        Vi[(opcode & 0x0F00) >> 8] &= Vi[(opcode & 0x00F0) >> 4]
        PC += 2
    if (opcode & 0xF00F) == 0x8003:
        Vi[(opcode & 0x0F00) >> 8] ^= Vi[(opcode & 0x00F0) >> 4]
        PC += 2
    if (opcode & 0xF00F) == 0x8004:
        if Vi[(opcode & 0x0F00) >> 8] + Vi[(opcode & 0x00F0) >> 4] > 0xFF:
            Vi[0xF] = 1
        else:
            Vi[0xF] = 0
        Vi[(opcode & 0x0F00) >> 8] += Vi[(opcode & 0x00F0) >> 4]
        Vi[(opcode & 0x0F00) >> 8] &= 0xFF
        PC += 2
    if (opcode & 0xF00F) == 0x8005:
        if Vi[(opcode & 0x0F00) >> 8] > Vi[(opcode & 0x00F0) >> 4]:
            Vi[0xF] = 1
        else:
            Vi[0xF] = 0
        Vi[(opcode & 0x0F00) >> 8] -= Vi[(opcode & 0x00F0) >> 4]
        Vi[(opcode & 0x0F00) >> 8] &= 0xFF
        PC += 2
    if (opcode & 0xF00F) == 0x8006:
        Vi[0xF]=(Vi[(opcode & 0x0F00) >> 8]&0x1)
        Vi[(opcode & 0x0F00)>> 8] = Vi[(opcode & 0x0F00) >> 8] >> 1
        Vi[(opcode & 0x0F00) >> 8] &= 0xFF
        PC += 2
    if (opcode & 0xF00F) == 0x8007:
        if Vi[(opcode & 0x0F00) >> 8] < Vi[(opcode & 0x00F0) >> 4]:
            Vi[0xF] = 1
        else:
            Vi[0xF] = 0
        Vi[(opcode & 0x0F00) >> 8] = Vi[(opcode & 0x00F0) >> 4] - Vi[(opcode & 0x0F00) >> 8]
        Vi[(opcode & 0x0F00) >> 8] &= 0xFF
        PC += 2
    if (opcode & 0xF00F) == 0x800E:
        Vi[0xF]=(Vi[(opcode & 0x0F00) >> 8] >> 7)
        Vi[(opcode & 0x0F00) >> 8] = Vi[(opcode & 0x0F00) >> 8] << 1
        Vi[(opcode & 0x0F00) >> 8] &= 0xFF
        PC += 2
    if (opcode & 0xF000) == 0x9000:
        if Vi[(opcode & 0x0F00) >> 8] != Vi[(opcode & 0x00F0) >> 4]:
            PC += 4
        else:
            PC += 2
    if (opcode & 0xF000) == 0xA000:
        I = opcode & 0x0FFF
        PC += 2
    if (opcode & 0xF000) == 0xB000:
        PC = (opcode & 0x0FFF) + Vi[0x0]
    if (opcode & 0xF000) == 0xC000:
        Vi[(opcode & 0x0F00) >> 8] = randint(0x0,0xFF) & (opcode & 0x00FF)
        PC += 2
    if (opcode & 0xF000) == 0xD000:
        B = 0
        for yline in range((opcode&0x000F)):
            for xline in range(7,-1,-1):
                X,Y = Vi[(opcode & 0x0F00) >> 8] + 7 - xline, Vi[(opcode & 0x00F0) >> 4] + yline 
                if (Memory[I + yline] >> xline) & 0x1 == 1 and ((X > 63 and Vi[(opcode & 0x0F00) >> 8] > 63) or (Y > 31 and Vi[(opcode & 0x00F0) >> 4] > 31) or (X <= 63) or (Y<= 31)):         
                    if gfx[64*(Y - 32*(Y//32)) + X - 64*(X//64)] == 1:
                        Vi[0xF] = 1
                        B += 1
                    gfx[64*(Y - 32*(Y//32)) + X - 64*(X//64)] ^= 1
        if not B:
            Vi[0xF] = 0
        PC += 2
    if (opcode & 0xF00F) == 0xE00E:
        if key_inputs[Vi[(opcode & 0x0F00) >> 8]]:
            PC += 4
        else:
            PC += 2
    if (opcode & 0xF00F) == 0xE001:
        if key_inputs[Vi[(opcode & 0x0F00) >> 8]]:
            PC += 2
        else:
            PC += 4
    if (opcode & 0xF0FF) == 0xF007:
        Vi[(opcode & 0x0F00) >> 8] = delay_timer
        PC += 2
    if (opcode & 0xF0FF) == 0xF00A:
        if 1 in key_inputs:
            Vi[(opcode & 0x0F00) >> 8] = key_inputs.index(1)
            PC += 2
    if (opcode & 0xF0FF) == 0xF015:
        delay_timer = Vi[(opcode & 0x0F00) >> 8]
        PC += 2
    if (opcode & 0xF0FF) == 0xF018:
        sound_timer = Vi[(opcode & 0x0F00) >> 8]
        PC += 2
    if (opcode & 0xF0FF) == 0xF01E:
        I += Vi[(opcode & 0x0F00) >> 8]
        PC += 2
    if (opcode & 0xF0FF) == 0xF029:
        I = (Vi[(opcode & 0x0F00) >> 8] * 5) & 0xfff
        PC += 2
    if (opcode & 0xF0FF) == 0xF033:
        Memory[I] = Vi[(opcode & 0x0F00) >> 8] // 100
        Memory[I+1] = (Vi[(opcode & 0x0F00) >> 8]%100)//10
        Memory[I+2] = Vi[(opcode & 0x0F00) >> 8]%10
        PC += 2
    if (opcode & 0xF0FF) == 0xF055:
        for x in range(((opcode & 0x0F00) >> 8) + 1):
            Memory[I + x] = Vi[x]
        PC += 2
    if (opcode & 0xF0FF) == 0xF065:
        for x in range(((opcode & 0x0F00) >> 8) + 1):
            Vi[x] = Memory[I + x]
        PC += 2
def Draw():
    global DISPLAYSURF,Pixelsize,gfx
    i = 0
    for x in gfx:
        if x:
            pygame.draw.rect(DISPLAYSURF,(255,255,255),((i%64)*Pixelsize,(i//64)*Pixelsize,Pixelsize,Pixelsize))
        i += 1
def Decreasetimers():
    global delay_timer,sound_timer,sound,t
    if time.time() - t >= 1/60:
        if delay_timer > 0:
            delay_timer -= 1
        if sound_timer > 0:
            sound_timer -= 1
            if sound_timer <= 0:
                sound.play()
        t = time.time()
while True:
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == pygame.K_1:
                key_inputs[0x1] = 1
            if event.key == pygame.K_2:
                key_inputs[0x2] = 1
            if event.key == pygame.K_3:
                key_inputs[0x3] = 1
            if event.key == pygame.K_4:
                key_inputs[0xC] = 1
            if event.key == pygame.K_q:
                key_inputs[0x4] = 1
            if event.key == pygame.K_w:
                key_inputs[0x5] = 1
            if event.key == pygame.K_e:
                key_inputs[0x6] = 1
            if event.key == pygame.K_r:
                key_inputs[0xD] = 1
            if event.key == pygame.K_a:
                key_inputs[0x7] = 1
            if event.key == pygame.K_s:
                key_inputs[0x8] = 1
            if event.key == pygame.K_d:
                key_inputs[0x9] = 1
            if event.key == pygame.K_f:
                key_inputs[0xE] = 1
            if event.key == pygame.K_z:
                key_inputs[0xA] = 1
            if event.key == pygame.K_x:
                key_inputs[0x0] = 1
            if event.key == pygame.K_c:
                key_inputs[0xB] = 1
            if event.key == pygame.K_v:
                key_inputs[0xF] = 1
        if event.type == KEYUP:
            if event.key == pygame.K_1:
                key_inputs[0x1] = 0
            if event.key == pygame.K_2:
                key_inputs[0x2] = 0
            if event.key == pygame.K_3:
                key_inputs[0x3] = 0
            if event.key == pygame.K_4:
                key_inputs[0xC] = 0
            if event.key == pygame.K_q:
                key_inputs[0x4] = 0
            if event.key == pygame.K_w:
                key_inputs[0x5] = 0
            if event.key == pygame.K_e:
                key_inputs[0x6] = 0
            if event.key == pygame.K_r:
                key_inputs[0xD] = 0
            if event.key == pygame.K_a:
                key_inputs[0x7] = 0
            if event.key == pygame.K_s:
                key_inputs[0x8] = 0
            if event.key == pygame.K_d:
                key_inputs[0x9] = 0
            if event.key == pygame.K_f:
                key_inputs[0xE] = 0
            if event.key == pygame.K_z:
                key_inputs[0xA] = 0
            if event.key == pygame.K_x:
                key_inputs[0x0] = 0
            if event.key == pygame.K_c:
                key_inputs[0xB] = 0
            if event.key == pygame.K_v:
                key_inputs[0xF] = 0
    DISPLAYSURF.fill((0,0,0))
    if time.time() - t > freq:
        emulateCPU()
    Draw()
    Decreasetimers()
    pygame.display.update()
    
