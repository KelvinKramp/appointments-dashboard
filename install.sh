#!/bin/sh
echo "removing build folder"
rm -rf build
echo "removing dist folder"
rm -rf dist
echo "removing secrets file"
rm secrets.json
echo "removing old ZIP file"
rm RBH_app.zip

echo "creating main executable file "
pyinstaller --onefile --noconfirm -w --debug=all main.py
echo "moving main executable file"
mv ./dist/main ./main
rm main.spec

echo "creating directory with files for application"
pyinstaller --onedir --noconfirm -w --debug=all dash_app.spec
echo "moving main executable to directory"
mv ./main ./dist/dash_app/
mv ./dist/dash_app/ ./RBH_app
echo "zipping RBH app into RBH_app.zip file"
zip -r RBH_app.zip ./RBH_app
echo "removing RBH_app folder"
rm -rf ./RBH_app
echo "removing build folder"
rm -rf build
echo "removing dist folder"
rm -rf dist
echo "installation completed, press enter to continue"
read input
