"""
/***************************************************************************
        begin                : 2016-01-05
        copyright            : (C) 2016 by BGEO SL
        email                : vicente.medina@gits.ws
        git sha              : $Format:%H$
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

# -*- coding: utf-8 -*-
from qgis.core import QgsPoint, QgsFeatureRequest, QgsExpression
from qgis.gui import QgsVertexMarker
from PyQt4.QtCore import QPoint, Qt 
from PyQt4.QtGui import QApplication, QColor, QAction, QPushButton, QDateEdit, QTimeEdit
from PyQt4.Qt import  QDate, QTime

from map_tools.parent import ParentMapTool

from ..ui.mincut import Mincut
from ..ui.mincut_fin import Mincut_fin

from datetime import *


import utils_giswater


class MincutMapTool(ParentMapTool):
    ''' Button 26. User select one node or arc.
    Execute SQL function: 'gw_fct_mincut'
    This function fills 3 temporary tables with id's: node_id, arc_id and valve_id
    Returns and integer: error code
    Get these id's and select them in its corresponding layers '''    

    def __init__(self, iface, settings, action, index_action):  
        ''' Class constructor '''
        
        # Call ParentMapTool constructor     
        super(MincutMapTool, self).__init__(iface, settings, action, index_action)  

        # Vertex marker
        self.vertexMarker = QgsVertexMarker(self.canvas)
        self.vertexMarker.setColor(QColor(255, 25, 25))
        self.vertexMarker.setIconSize(11)
        self.vertexMarker.setIconType(QgsVertexMarker.ICON_BOX) # or ICON_CROSS, ICON_X
        self.vertexMarker.setPenWidth(5)
       
        
        
    ''' QgsMapTools inherited event functions '''

    def canvasMoveEvent(self, event):

        # Hide highlight
        self.vertexMarker.hide()

        # Get the click
        x = event.pos().x()
        y = event.pos().y()

        #Plugin reloader bug, MapTool should be deactivated
        try:
            eventPoint = QPoint(x, y)
        except(TypeError, KeyError):
            self.iface.actionPan().trigger()
            return

        # Snapping        
        (retval,result) = self.snapper.snapToBackgroundLayers(eventPoint)   #@UnusedVariable   
        self.current_layer = None

        # That's the snapped point
        if result <> []:

            # Check Arc or Node
            for snapPoint in result:

                exist_node = self.snapperManager.check_node_group(snapPoint.layer)
                exist_arc  = self.snapperManager.check_arc_group(snapPoint.layer)

                if exist_node or exist_arc:
                #if snapPoint.layer.name() == self.layer_node.name() or snapPoint.layer.name() == self.layer_arc.name():
                    
                    # Get the point
                    point = QgsPoint(result[0].snappedVertex)

                    # Add marker
                    self.vertexMarker.setCenter(point)
                    self.vertexMarker.show()

                    # Data for function
                    self.current_layer = result[0].layer
                    self.snappFeat = next(result[0].layer.getFeatures(QgsFeatureRequest().setFilterFid(result[0].snappedAtGeometry)))

                    # Change symbol
                    if exist_node:
                        self.vertexMarker.setIconType(QgsVertexMarker.ICON_CIRCLE)
                    else:
                        self.vertexMarker.setIconType(QgsVertexMarker.ICON_BOX)

                    break


    def canvasReleaseEvent(self, event):
        ''' With left click the digitizing is finished '''
        
        if event.button() == Qt.LeftButton and self.current_layer is not None:

            # Get selected layer type: 'arc' or 'node'
    
            if self.snapperManager.check_arc_group(self.current_layer):
                elem_type = 'arc'
            elif self.snapperManager.check_node_group(self.current_layer):
                elem_type = 'node'
            else:
                message = "Current layer not valid"
                self.controller.show_warning(message, context_name='ui_message')
                return

            feature = self.snappFeat
            elem_id = feature.attribute(elem_type+'_id')

            # Execute SQL function
            function_name = "gw_fct_mincut"
            sql = "SELECT "+self.schema_name+"."+function_name+"('"+str(elem_id)+"', '"+elem_type+"');"

            # Change cursor
            QApplication.setOverrideCursor(Qt.WaitCursor)

            result = self.controller.execute_sql(sql)
            if result:
                # Get 'arc' and 'node' list and select them
                self.mg_mincut_select_features()

            # Old cursor
            QApplication.restoreOverrideCursor()

            # Refresh map canvas
            self.iface.mapCanvas().refreshAllLayers()

            for layerRefresh in self.iface.mapCanvas().layers():
                layerRefresh.triggerRepaint()


    def mg_mincut_select_features(self):

        sql = "SELECT * FROM "+self.schema_name+".anl_mincut_arc ORDER BY arc_id"
        rows = self.controller.get_rows(sql)
        if rows:
    
            # Build an expression to select them
            aux = "\"arc_id\" IN ("
            for elem in rows:
                aux += "'" + elem[0] + "', "
            aux = aux[:-2] + ")"

            # Get a featureIterator from this expression:
            expr = QgsExpression(aux)
            if expr.hasParserError():
                message = "Expression Error: " + str(expr.parserErrorString())
                self.controller.show_warning(message, context_name='ui_message')
                return

            for layer_arc in self.layer_arc_man:

                it = layer_arc.getFeatures(QgsFeatureRequest(expr))
    
                # Build a list of feature id's from the previous result
                id_list = [i.id() for i in it]

                # Select features with these id's
                layer_arc.setSelectedFeatures(id_list)

        sql = "SELECT * FROM " + self.schema_name + ".anl_mincut_node ORDER BY node_id"
        rows = self.controller.get_rows(sql)
        if rows:

            # Build an expression to select them
            aux = "\"node_id\" IN ("
            for elem in rows:
                aux += "'" + elem[0] + "', "
            aux = aux[:-2] + ")"

            # Get a featureIterator from this expression:
            expr = QgsExpression(aux)
            if expr.hasParserError():
                message = "Expression Error: " + str(expr.parserErrorString())
                self.controller.show_warning(message, context_name='ui_message')
                return

            for layer_node in self.layer_node_man:

                it = layer_node.getFeatures(QgsFeatureRequest(expr))

                # Build a list of feature id's from the previous result
                id_list = [i.id() for i in it]

                # Select features with these id's
                layer_node.setSelectedFeatures(id_list)


    def mincut(self):
        ''' mincut function'''
        print "mincut"
        
        # Store user snapping configuration
        self.snapperManager.storeSnappingOptions()

        # Clear snapping
        self.snapperManager.clearSnapping()

        # Set snapping to arc and node
        self.snapperManager.snapToArc()
        self.snapperManager.snapToNode()

        # Change cursor
        self.canvas.setCursor(self.cursor)

        # Show help message when action is activated
        if self.show_help:
            message = "Select a node or pipe and click on it, the valves minimum cut polygon is computed"
            self.controller.show_info(message, context_name='ui_message' )

        # Control current layer (due to QGIS bug in snapping system)
        if self.canvas.currentLayer() == None:
            self.iface.setActiveLayer(self.layer_node_man[0])
        
        
    def mincut2(self):
        print "valve analytics"
        
    def config(self):
        print "mconfig"
        
    def real_start(self):
       
        #date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #print date
        
        self.date_start = QDate.currentDate()
        self.cbx_date_start.setDate(self.date_start)
        
        self.time_start = QTime.currentTime()
        self.cbx_hours_start.setTime(self.time_start)
        
        self.btn_end.setEnabled(True)   
        
       
    def real_end(self):

        self.date_end = QDate.currentDate()
        self.cbx_date_end.setDate(self.date_end)
        
        self.time_end = QTime.currentTime()
        self.cbx_hours_end.setTime(self.time_end)
        
        # Create the dialog and signals
        self.dlg_fin = Mincut_fin()
        utils_giswater.setDialog(self.dlg_fin)
        
        self.cbx_date_start_fin = self.dlg_fin.findChild(QDateEdit, "cbx_date_start_fin")
        self.cbx_hours_start_fin = self.dlg_fin.findChild(QTimeEdit, "cbx_hours_start_fin")
        self.cbx_date_start_fin.setDate(self.date_start)
        self.cbx_hours_start_fin.setTime(self.time_start)
        
        self.cbx_date_end_fin = self.dlg_fin.findChild(QDateEdit, "cbx_date_end_fin")
        self.cbx_hours_end_fin = self.dlg_fin.findChild(QTimeEdit, "cbx_hours_end_fin")
        self.cbx_date_end_fin.setDate(self.date_end)
        self.cbx_hours_end_fin.setTime(self.time_end)      
        
        # Open the dialog
        self.dlg_fin.show() 
        
        
    def activate(self):

        # Check button
        self.action().setChecked(True)
        print "test"
        # Create the dialog and signals
        self.dlg = Mincut()
        utils_giswater.setDialog(self.dlg)
        
        #self.dlg.findChild(QPushButton, "btn_start").clicked.connect(self.real_start)
        self.btn_start = self.dlg.findChild(QPushButton, "btn_start")  
        self.btn_start.clicked.connect(self.real_start)
        #self.dlg.findChild(QPushButton, "btn_end").clicked.connect(self.real_end)
        self.btn_end = self.dlg.findChild(QPushButton, "btn_end")  
        self.btn_end.clicked.connect(self.real_end)
               
        # Toolbar actions
        self.dlg.findChild(QAction, "actionConfig").triggered.connect(self.config)
        self.dlg.findChild(QAction, "actionMincut").triggered.connect(self.mincut)
        self.dlg.findChild(QAction, "actionMincut2").triggered.connect(self.mincut2)
        
        self.cbx_date_start = self.dlg.findChild(QDateEdit, "cbx_date_start")
        self.cbx_hours_start = self.dlg.findChild(QTimeEdit, "cbx_hours_start")
        
        self.cbx_date_end = self.dlg.findChild(QDateEdit, "cbx_date_end")
        self.cbx_hours_end = self.dlg.findChild(QTimeEdit, "cbx_hours_end")
            
        # Open the dialog
        self.dlg.show() 
        

    def deactivate(self):

        # Check button
        self.action().setChecked(False)

        # Restore previous snapping
        self.snapperManager.recoverSnappingOptions()

        # Recover cursor
        self.canvas.setCursor(self.stdCursor)

        # Remove highlight
        self.h = None
        
        