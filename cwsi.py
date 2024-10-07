# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CWSI - a QGIS plugin 
                               
 This plugin calculates the crop water stress index (CWSI) from thermal images.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-10-17
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Florian Ellsäßer
        email                : info@ecothermographylab.com
        
More information: https://github.com/FloEll/CWSI_plugin

This is still an experimental version and I don't claim that it is perfect 
yet. If you spot bugs or problems with the method, please contact me! I'm 
always happy to improve this software. 

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# Import libraries
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog
from qgis.core import QgsProject, Qgis, QgsRasterLayer

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .cwsi_dialog import CWSIDialog
import os.path
# Import Libraries for the CWSI
import gdal
import numpy as np

class CWSI:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'CWSI_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&CWSI')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('CWSI', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/cwsi/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'This plugin calculates the CWSI from thermal images.'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&CWSI'),
                action)
            self.iface.removeToolBarIcon(action)
            
    def select_input_file(self):
        '''Opens a file browser and populates the output_name lineEdit widget
        with the file path and name the user chose'''
        file_name, _filter = QFileDialog.getOpenFileName(
                self.dlg, 'Select input raster name','','*.tif')
        base_name = file_name
        self.dlg.input_name.setText(file_name)
        in_raster = QgsRasterLayer(file_name, base_name)
        QgsProject.instance().addMapLayer(in_raster)
        
    def select_output_raster_file(self):
        '''Opens a file browser and populates the output_name lineEdit widget
        with the file path and name the user chose'''
        filename, _filter = QFileDialog.getSaveFileName(
                self.dlg, 'Select output raster name','','*.tif')
        self.dlg.output_raster_name.setText(filename)
            
    def select_output_file(self):
        '''Opens a file browser and populates the output_name lineEdit widget
        with the file path and name the user chose'''
        filename, _filter = QFileDialog.getSaveFileName(
                self.dlg, 'Select output file name','','*.csv')
        self.dlg.output_name.setText(filename) 
        
    def read_lst_img(self,in_file, na_val=None):
        '''This function reads thermal image and extracts land sturface 
        temperature (lst) projection (prj) and georeference data (geo).
        :in_file : path and file name
        :na_val : float that specifies NaN values
        '''            
        new_raster = gdal.Open(in_file,gdal.GA_ReadOnly)
        
        self.dlg.lst = new_raster.GetRasterBand(1).ReadAsArray()
        # if input is in Kelvin, convert to °C
        if np.mean(self.dlg.lst) > 180.0:
            self.dlg.lst = self.dlg.lst - 273.15
        self.dlg.prj = new_raster.GetProjection()
        self.dlg.geo = new_raster.GetGeoTransform()
        self.dlg.lon = float(self.dlg.geo[0])
        self.dlg.lat = float(self.dlg.geo[3])
        # set all zeros to NaN
        self.dlg.lst[self.dlg.lst == 0.0] = self.dlg.na_val
        
    def get_model_parameters(self,in_file):
        '''This function reads the input of the gui and assigns it to the parameters'''
        self.dlg.na_val = None
        #input
        self.read_lst_img(in_file) # read the lst image
        self.dlg.twet = self.dlg.twet_input.text()
        self.dlg.tdry = self.dlg.tdry_input.text()
        self.dlg.tair = self.dlg.tair_input.text()
        self.dlg.tair_increase = self.dlg.tair_increase_input.text()
        
        
        # results
        self.dlg.cwsi = None # cwsi map 

    def get_tdry_twet(self):
        '''This function defines tmin and tmax (minimum and maximum temperatures) 
        from the gui input or from the image itself
        '''
        # get Twet
        if self.dlg.twet == '':
            self.dlg.twet  = float(np.quantile(self.dlg.lst[~np.isnan(self.dlg.lst)], 0.05))
        else:
            self.dlg.twet = float(self.dlg.twet)
            
        # get Tdry
        # first check if sb. measured Tdry
        if self.dlg.tdry == '':
            if self.dlg.tair != '':
                self.dlg.tdry = float(self.dlg.tair) + float(self.dlg.tair_increase)
            else:
                self.dlg.tdry  = float(np.quantile(self.dlg.lst[~np.isnan(self.dlg.lst)],0.95))
    
        else:
            self.dlg.tdry = float(self.dlg.tdry)
            
        
    def get_cwsi(self):
        '''This function calculates the cwsi after Jones (1992 eq. 9.6; 1999)
        '''
        if self.dlg.cwsi == None:
            self.dlg.cwsi = (self.dlg.lst - self.dlg.twet)/(self.dlg.tdry - self.dlg.twet)
                             
            # for values that are too big or too small to fit the index
            self.dlg.cwsi[self.dlg.cwsi >= 1.0] = 1.0
            self.dlg.cwsi[self.dlg.cwsi <= 0.0] = 0.0            
            
        else: 
            pass
        
    def write_output_images(self):
        '''This function writes the output data into a GeoTIFF'''
        
        rows,cols=np.shape(self.dlg.lst)
        driver = gdal.GetDriverByName('GTiff')
        nbands=1
        
        out_raster = driver.Create(self.dlg.output_raster_name.text(), cols, 
                                   rows, nbands, gdal.GDT_Float32)
        out_raster.SetGeoTransform(self.dlg.geo)
        out_raster.SetProjection(self.dlg.prj)
        # Write cwsi to band 1
        band_1=out_raster.GetRasterBand(1)
        band_1.SetNoDataValue(0)
        band_1.WriteArray(self.dlg.cwsi)
        band_1.FlushCache()
                                
        # Flush Cache
        out_raster.FlushCache()
        del out_raster
        
        # load layer into qgis
        qgis_raster = QgsRasterLayer(self.dlg.output_raster_name.text(), 'CWSI Output')
        QgsProject.instance().addMapLayer(qgis_raster)
        
    def write_stats(self,file,flux_name,flux):
        file.write(flux_name + ' ' + str(np.mean(flux[~np.isnan(flux)])) + ' ' +
                              str(np.min(flux[~np.isnan(flux)])) + ' ' +
                              str(np.max(flux[~np.isnan(flux)])) + '\n'
                              )
        
    def write_output_stats(self):
        # write the output data in a .csv file
        with open(self.dlg.output_name.text(), 'w') as output_file:
            # write an out file with the most important stats
            # model parameters
            output_file.write('Model parameters:' + '\n')
            output_file.write('Twet: ' + str(self.dlg.twet) + '\n')
            output_file.write('Tdry: ' + str(self.dlg.tdry) + '\n')
            output_file.write('Tair: ' + str(self.dlg.tair) + '\n')
            output_file.write('Tair increase: ' + str(self.dlg.tair_increase) + '\n')
            output_file.write('temp mean: ' + str(np.mean(self.dlg.lst[~np.isnan(self.dlg.lst)])) + '\n')
            output_file.write('5% quantile: ' + str(np.quantile(self.dlg.lst[~np.isnan(self.dlg.lst)],0.05)) + '\n')
            output_file.write('95% quantile: ' + str(np.quantile(self.dlg.lst[~np.isnan(self.dlg.lst)],0.95)) + '\n')
            output_file.write('CWSI mean: ' + str(np.mean(self.dlg.cwsi[~np.isnan(self.dlg.cwsi)])) + '\n')
            output_file.write('5% quantile: ' + str(np.quantile(self.dlg.cwsi[~np.isnan(self.dlg.cwsi)],0.05)) + '\n')
            output_file.write('95% quantile: ' + str(np.quantile(self.dlg.cwsi[~np.isnan(self.dlg.cwsi)],0.95)) + '\n')
            output_file.write('type ' + 'mean ' + 'min ' + 'max ' + '\n')
            self.write_stats(output_file,'Temperature [°C]',self.dlg.lst)
            self.write_stats(output_file,'CWSI [-]',self.dlg.cwsi)
    
    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = CWSIDialog()
            self.dlg.search_input_button.clicked.connect(self.select_input_file)
            self.dlg.search_output_raster_button.clicked.connect(self.select_output_raster_file)
            self.dlg.search_output_button.clicked.connect(self.select_output_file)
            
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # define in raster
            in_file = self.dlg.input_name.text()
            # get all the model parameters
            self.get_model_parameters(in_file)
            # get tdry and twet if not already defined in settings
            self.get_tdry_twet()
            # calculate the cwsi
            self.get_cwsi()
            # write results to a .tif file and load it into qgis
            self.write_output_images()
            # write output stats file 
            self.write_output_stats()
                         
            # Display a push message that QWaterModel was successful
            self.iface.messageBar().pushMessage(
                    'Success', 'The CWSI was calculated successfully!',
                    level=Qgis.Success, duration=3) 
            
            
