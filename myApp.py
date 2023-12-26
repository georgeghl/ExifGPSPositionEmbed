from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QMessageBox, QFileDialog, QGraphicsScene
from PyQt5.QtGui import QPixmap, QImage
import sys
import os
import time
import json
import cv2
import myGui

class myAppMainWindow(QMainWindow):
    # Define value names
    jsonFilePath=""
    jsonFileType=""
    imgFilePath=""
    imgFileType=""
    locationData={}
    provinceName=""
    cityName=""
    districtName=""
    siteName=""
    GPSLocation={}
    
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)
        self.ui = myGui.myGuiMainWindow()
        self.ui.setupUi(self)
        
        self.scene = QGraphicsScene()  # 创建画布
        self.ui.graphicsViewImgPreview.setScene(self.scene)  # 把画布添加到窗口
        self.ui.graphicsViewImgPreview.show()
        
        
        # Binding Button Setup
        self.ui.pushButtonSelectJsonFile.released.connect(self.selectJsonFile)
        self.ui.pushButtonSelectImgFile.released.connect(self.selectImgFile)
        self.ui.pushButtonStart.released.connect(self.startProcess)
        
        # Binding QComboBox Setup
        self.ui.comboBoxProvince.activated.connect(self.showCity)
        self.ui.comboBoxCity.activated.connect(self.showDistrict)
        self.ui.comboBoxDistrict.activated.connect(self.showSite)
        self.ui.comboBoxSite.activated.connect(self.setGPSLocation)
        
        
    def selectJsonFile(self):
        print("selectJsonFile Clicked")
        jsonFilePath,jsonFileType = QFileDialog.getOpenFileName(self, "选取文件", os.getcwd(), 
        "Json Files(*.json)")
        if not os.path.exists(jsonFilePath):
            self.ui.labelJsonFileName.setText("File DO NOT Exist!!!")
            return
        self.jsonFilePath=jsonFilePath
        self.ui.labelJsonFileName.setText(self.jsonFilePath)
        if not jsonFilePath.split(".")[-1].lower()=="json":
            self.ui.labelJsonFileName.setText("NOT a json file!!!")
            return
        self.jsonFileType=jsonFileType
        print(self.jsonFilePath, self.jsonFileType)
        with open(file=self.jsonFilePath,mode="r",encoding="utf-8") as f:
            self.locationData=json.load(f)
        self.ui.comboBoxProvince.clear()
        self.ui.comboBoxProvince.addItems(self.locationData.keys())
    
    # Change Values of ComboBox
    def showCity(self):
        self.provinceName=self.ui.comboBoxProvince.currentText()
        print("Current province name: ", self.provinceName)
        self.ui.comboBoxCity.clear()
        self.ui.comboBoxCity.addItems(self.locationData[self.provinceName].keys())
    def showDistrict(self):
        self.cityName=self.ui.comboBoxCity.currentText()
        print("Current city name: ", self.cityName)
        self.ui.comboBoxDistrict.clear()
        self.ui.comboBoxDistrict.addItems(self.locationData[self.provinceName][self.cityName].keys())
    def showSite(self):
        self.districtName=self.ui.comboBoxDistrict.currentText()
        print("Current province name: ", self.districtName)
        self.ui.comboBoxSite.clear()
        self.ui.comboBoxSite.addItems(self.locationData[self.provinceName][self.cityName][self.districtName].keys())
        
    # Set Location GPS Value
    def setGPSLocation(self):
        self.siteName=self.ui.comboBoxSite.currentText()
        print("Current Site Info: ",self.provinceName, self.cityName, self.districtName, self.siteName)
        self.GPSLocation=self.locationData[self.provinceName][self.cityName][self.districtName][self.siteName]
        print(self.GPSLocation)
        
        
    def selectImgFile(self):
        print("selectImgFile Clicked")
        imgFilePath,imgFileType = QFileDialog.getOpenFileName(self, "选取文件", os.getcwd(), 
        "Image Files(*.jpg *.jpeg *.JPG *.JPEG);;All Files(*)")
        if not os.path.exists(imgFilePath):
            self.ui.labelImgFileName.setText("File DO NOT Exist!!!")
            return
        self.imgFilePath=imgFilePath
        self.ui.labelImgFileName.setText(self.imgFilePath)
        if not imgFilePath.split(".")[-1].lower()=="jpg" or imgFilePath.split(".")[-1].lower()=="jpeg":
            self.ui.labelImgFileName.setText("NOT a image file!!!")
            return
        self.imgFileType=imgFileType
        print(self.imgFilePath, self.imgFileType)
        img = cv2.imread(imgFilePath)
        cvimg = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 把opencv 默认BGR转为通用的RGB
        y, x = img.shape[:-1]
        frame = QImage(cvimg, x, y, QImage.Format_RGB888)
        self.scene.clear()  #先清空上次的残留
        self.pix = QPixmap.fromImage(frame).scaled(600,  400)
        self.scene.addPixmap(self.pix)
        
    def startProcess(self):
        print("startProcess Clicked")
        self.ui.labelStartProcess.setText("Processing, Please Wait......")
        self.processFunc()
        # 手动加延迟
        time.sleep(1)
        self.ui.labelStartProcess.setText("Succeed!")
        
    def processFunc(self):
        osName=os.name
        sysPlatform=sys.platform
        print("OS: "+osName+", Platform: "+sysPlatform)
        # Default Value
        GPSLatitudeRef="N"
        GPSLongitudeRef="E"
        GPSAltitudeRef="0"
        # GPS Location of East Gate, Chongqing University, Huxi Campus, Chongqing China.
        # Format: ° ' '' , fraction
        GPSLatitude=self.GPSLocation["Latitude"]
        GPSLongitude=self.GPSLocation["Longtitude"]
        GPSAltitude=self.GPSLocation["Altitude"]

        # Image File Path
        imgPath=self.imgFilePath

        # Suffix Differs from Platform
        absPath=os.getcwd()
        # print(absPath)
        if sysPlatform.startswith("linux"):
            # suffix=absPath+"/exiv2linux/exiv2 "
            suffix=absPath+"./exiv2linux/bin/exiv2 "
        elif sysPlatform.startswith("win"):
            # suffix=absPath+"\\exiv2win\\bin\\exiv2.exe "
            suffix=absPath+"./exiv2win/bin/exiv2.exe "

        # Execution command
        cmdGPSLatitude =" -M \"set Exif.GPSInfo.GPSLatitude "+GPSLatitude+"\" -M \"set Exif.GPSInfo.GPSLatitudeRef "+GPSLatitudeRef+"\" "
        cmdGPSLongitude =" -M \"set Exif.GPSInfo.GPSLongitude "+GPSLongitude+"\" -M \"set Exif.GPSInfo.GPSLongitudeRef "+GPSLongitudeRef+"\" "
        cmdGPSAltitude =" -M \"set Exif.GPSInfo.GPSAltitude "+GPSAltitude+"\" -M \"set Exif.GPSInfo.GPSAltitudeRef "+GPSAltitudeRef+"\" "

        command=suffix+cmdGPSLatitude+imgPath
        print(command)
        os.system(command)
        command=suffix+cmdGPSLongitude+imgPath
        print(command)
        os.system(command)
        command=suffix+cmdGPSAltitude+imgPath
        print(command)
        os.system(command)
        
        
def main():
    myApp = QApplication(sys.argv)
    myMainWindow = myAppMainWindow()
    myMainWindow.show()
    sys.exit(myApp.exec_())
    
if __name__=="__main__":
    main()