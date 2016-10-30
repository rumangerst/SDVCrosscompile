@echo off

set sd=%~dp0

python %sd%\xcompile.py --lib-windows %sd%\lib-windows --lib-linux %sd%\lib-linux --lib-mac %sd%\lib-mac %*