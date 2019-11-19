import pygame, sys, codecs, configparser, os, datetime, time, re
from textwrap import wrap

zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')

def is_contains_chinese(strs):
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False

if __name__ == "__main__":

    white = 255, 255, 255
    black = 0, 0, 0
    batBlackimage = pygame.image.load("./assets/blackbat.png")
    batWhiteimage = pygame.image.load("./assets/whitebat.png")

    Battery = "/sys/class/power_supply/axp20x-battery/uevent"

    EnglishMode = False

    pygame.init()

    textPath = sys.argv[1]
    cfgPath = textPath + ".ini"

    firstPartText = ""
    secondPartText = ""

    screen = pygame.display.set_mode((320, 240))
    h1Front = pygame.font.Font("wqy-zenhei.ttc", 18)
    h0Front = pygame.font.Font("wqy-zenhei.ttc", 30)
    miniFont = pygame.font.Font("wqy-zenhei.ttc", 12)
    pFront = pygame.font.Font("wqy-zenhei.ttc", 14)
    titleText = "Gameshell Reader v0.5"

    clock = pygame.time.Clock()

    try:
        fileSize = os.stat(textPath).st_size/(1024*1024.0)
        f = codecs.open(textPath, 'r', 'utf-8')
        readTxt = f.read()
        f.close()
    except Exception as e:
        screen.fill(white)
        offset = 0
        lines = wrap(str(e), 21)
        totalLines = len(lines)
        textImage = pFront.render("Error loading text file. Please use a valid text", True, black)
        screen.blit(textImage, (10,2))
        textImage = pFront.render("file that's in UTF-8 encoding. Error message:", True, black)
        screen.blit(textImage, (10, 16))
        for x in range(0, 11):
            if x + offset < totalLines:
                textImage = pFront.render(lines[x + offset], True, black)
                screen.blit(textImage, (10, x * 17 + 40))
                lastline = x + offset + 1
        pygame.display.update()
        while True:
            clock.tick(5)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        quit()
                        break

    if not is_contains_chinese(readTxt):
        EnglishMode = True

    screen.fill(white)
    titleImg = h0Front.render("Gameshell Reader", True, black)
    screen.blit(titleImg, (38, 60))
    if EnglishMode:
        titleImg = pFront.render("Version 0.5  English Mode", True, black)
        screen.blit(titleImg, (120, 90))
    else:
        titleImg = pFront.render("Version 0.5  中文模式", True, black)
        screen.blit(titleImg, (145, 90))
    titleImg = pFront.render("Hello! Loading", True, black)
    screen.blit(titleImg, (2, 179))
    titleImg = pFront.render(os.path.basename(textPath), True, black)
    screen.blit(titleImg, (2, 195))
    titleImg = h1Front.render("Please wait...", True, black)
    screen.blit(titleImg, (2, 210))
    titleImg = miniFont.render("2019 LovelyA72", True, black)
    screen.blit(titleImg, (230, 220))
    pygame.display.update()
    clock.tick(2)
    #try:
        # or codecs.open on Python <= 2.5
        # or io.open on Python > 2.5 and <= 2.7
    #    filedata = open(filename, encoding='UTF-8').read()
    


    showBar = True

    config = configparser.ConfigParser()

    if not os.path.exists(cfgPath):
        config['Book'] = {
            'lastRead': "0"
        }
        with open(cfgPath, 'w') as configfile:
            config.write(configfile)

    config.read(cfgPath)
    offset = int(config["Book"]["lastRead"])

    if EnglishMode:
        lines = wrap(readTxt, 47)
    else:
        lines = wrap(readTxt, 21)


    FPS = 5

    totalLines = len(lines)
    lastline = 0

    nightMode = False

    noBat = False
    lowBat = False
    batPower = 0

    batUpdateCounter = 20
    batUpdateTime = 20

    while True:
        clock.tick(FPS)
        if batUpdateCounter != batUpdateTime:
            batUpdateCounter = batUpdateCounter + 1
        else:
            batUpdateCounter = 0
            try:
                bf = open(Battery)
            except IOError:
                noBat = True
            else:
                with bf:
                    bat_content = ""
                    bat_uevent = {}
                    bat_segs = [[0, 6], [7, 15], [16, 20], [21, 30], [31, 50], [51, 60], [61, 80], [81, 90], [91, 100]]
                    bat_content = bf.readlines()
                    bat_content = [x.strip() for x in bat_content]
                    bf.close()
                    for i in bat_content:
                        pis = i.split("=")
                        if len(pis) > 1:
                            bat_uevent[pis[0]] = pis[1]

                    if "POWER_SUPPLY_CAPACITY" in bat_uevent:
                        cur_cap = int(bat_uevent["POWER_SUPPLY_CAPACITY"])
                    else:
                        cur_cap = 0

                    # batPower = float(format((int(bat_uevent["POWER_SUPPLY_VOLTAGE_NOW"])/int(bat_uevent["POWER_SUPPLY_VOLTAGE_MAX_DESIGN"])) * 100, ".02f"))
                    batPower = str(cur_cap) + "%"
                    if cur_cap > 0 and cur_cap < 20:
                        lowBat = True
                    else:
                        lowBat = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                config['Book'] = {
                    'lastRead': str(offset)
                }
                with open(cfgPath, 'w') as configfile:
                    config.write(configfile)
                quit()
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    config['Book'] = {
                        'lastRead': str(offset)
                    }
                    with open(cfgPath, 'w') as configfile:
                        config.write(configfile)
                    quit()
                    break
                if event.key == pygame.K_SPACE:
                    showBar = not showBar
                    break
                if event.key == pygame.K_RETURN:
                    nightMode = not nightMode
                    if nightMode:
                        black = 255, 255, 255
                        white = 0, 0, 0
                    else:
                        white = 255, 255, 255
                        black = 0, 0, 0
                    break
                if event.key == pygame.K_RIGHT:
                    if totalLines < 11:
                        break
                    if offset > totalLines - 11:
                        offset = totalLines - 1
                    else:
                        offset = offset + 11
                    break
                if event.key == pygame.K_LEFT:
                    if totalLines < 11:
                        break
                    if offset < 11:
                        offset = 0
                    else:
                        offset = offset - 11
                    break
                if event.key == pygame.K_UP:
                    if totalLines < 11:
                        break
                    if offset == 0:
                        offset = 0
                        break
                    offset = offset - 1
                    break
                if event.key == pygame.K_DOWN:
                    if totalLines < 11:
                        break
                    if offset > totalLines - 2:
                        offset = totalLines - 1
                        break
                    offset = offset + 1
                    break

        screen.fill(white)
        # Print title bar
        if showBar:
            currentDT = datetime.datetime.now()
            if noBat:
                if nightMode:
                    pygame.draw.rect(screen, (80, 80, 80), (0, 0, 320, 20))
                else:
                    pygame.draw.rect(screen, (200, 200, 200), (0, 0, 320, 20))
                titleImg = miniFont.render(
                    titleText + "                                  " + currentDT.strftime("%H:%M"), True, black)
                screen.blit(titleImg, (10, 3))
            else:
                if nightMode:
                    pygame.draw.rect(screen, (80, 80, 80), (0, 0, 320, 20))
                    screen.blit(batWhiteimage, (200, 1))
                else:
                    pygame.draw.rect(screen, (200, 200, 200), (0, 0, 320, 20))
                    screen.blit(batBlackimage, (200, 1))
                titleImg = miniFont.render(
                    titleText + "                         " + str(batPower)
                    + "   " + currentDT.strftime("%H:%M"), True, black)
                screen.blit(titleImg, (10, 3))
        # Print book content
        for x in range(0, 11):
            if x + offset < totalLines:
                textImage = pFront.render(lines[x + offset], True, black)
                screen.blit(textImage, (10, x * 17 + 25))
                lastline = x + offset + 1
        if showBar:
            textImage = miniFont.render(str(int(offset / 10)) + "/" + str(int(totalLines / 10)) + " " + str(
                float("{0:.2f}".format(((lastline) / totalLines) * 100))) + "%", True, black)
            screen.blit(textImage, (10, 220))
        if lowBat:
            lowBatText = miniFont.render("(!)WARNING: LOW BATTERY", True, (255, 80, 10))
            screen.blit(lowBatText, (159, 220))

        pygame.display.update()
