pyi-makespec --noconsole --onefile ^
    --name=rock-paper-scissors-battle-royale ^
    --icon=icon.ico ^
    --splash splash.png ^
    --add-data=hitbox.png:. ^
    --add-data=overlay.png:. ^
    --add-data=paper.png:. ^
    --add-data=rock.png:. ^
    --add-data=scissors.png:. ^
    main.py

pyinstaller rock-paper-scissors-battle-royale.spec