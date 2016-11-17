# -*- coding: utf-8 -*-
"""
/***************************************************************************
 *                                                                         *
 *   This file is part of Giswater 2.0                                     *                                 *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.utils import iface
from qgis.gui import QgsMessageBar
from PyQt4.QtCore import QSettings, Qt
from PyQt4.QtGui import QLabel, QComboBox, QDateEdit, QPushButton, QLineEdit
from PyQt4.QtSql import QSqlTableModel

from functools import partial
import os.path
import sys  

import utils_giswater
from controller import DaoController

from ui.add_sum import Add_sum          # @UnresolvedImport
        
        
class ParentDialog(object):   
    
    def __init__(self, dialog, layer, feature):
        ''' Constructor class '''     
        self.dialog = dialog
        self.layer = layer
        self.feature = feature
        self.context_name = "ws_parent"    
        self.iface = iface    
        self.init_config()             
    
        
    def init_config(self):    
     
        # initialize plugin directory
        user_folder = os.path.expanduser("~") 
        self.plugin_name = 'giswater'  
        self.plugin_dir = os.path.join(user_folder, '.qgis2/python/plugins/'+self.plugin_name)    
        
        # Get config file
        setting_file = os.path.join(self.plugin_dir, 'config', self.plugin_name+'.config')
        if not os.path.isfile(setting_file):
            message = "Config file not found at: "+setting_file
            self.iface.messageBar().pushMessage(message, QgsMessageBar.WARNING, 5)  
            self.close()
            return
            
        self.settings = QSettings(setting_file, QSettings.IniFormat)
        self.settings.setIniCodec(sys.getfilesystemencoding())
        
        # Set controller to handle settings and database connection
        # TODO: Try to make only one connection
        self.controller = DaoController(self.settings, self.plugin_name, iface)
        status = self.controller.set_database_connection()      
        if not status:
            message = self.controller.getLastError()
            self.iface.messageBar().pushMessage(message, QgsMessageBar.WARNING, 5) 
            return 
             
        self.schema_name = self.settings.value("db/schema_name")           
        self.dao = self.controller.dao
  
        # Initialize variables            
        self.table_wjoin = self.schema_name+'."v_edit_man_wjoin"' 
        self.table_tap = self.schema_name+'."v_edit_man_tap"'
        self.table_greentap = self.schema_name+'."v_edit_man_greentap"'
        self.table_fountain = self.schema_name+'."v_edit_man_fountain"'
        
        self.table_tank = self.schema_name+'."v_edit_man_tank"'
        self.table_pump = self.schema_name+'."v_edit_man_pump"'
        self.table_source = self.schema_name+'."v_edit_man_source"'
        self.table_meter = self.schema_name+'."v_edit_man_meter"'
        self.table_junction = self.schema_name+'."v_edit_man_junction"'
        self.table_manhole = self.schema_name+'."v_edit_man_manhole"'
        self.table_reduction = self.schema_name+'."v_edit_man_reduction"'
        self.table_hydrant = self.schema_name+'."v_edit_man_hydrant"'
        self.table_valve = self.schema_name+'."v_edit_man_valve"'
        self.table_waterwell = self.schema_name+'."v_edit_man_waterwell"'
            
            
    def translate_form(self, context_name):
        ''' Translate widgets of the form to current language '''
        # Get objects of type: QLabel
        widget_list = self.dialog.findChildren(QLabel)
        for widget in widget_list:
            self.translate_widget(context_name, widget)
            
            
    def translate_widget(self, context_name, widget):
        ''' Translate widget text '''
        if widget:
            widget_name = widget.objectName()
            text = self.controller.tr(widget_name, context_name)
            if text != widget_name:
                widget.setText(text)         
         
       
    def load_tab_add_info(self):
        ''' Load data from tab 'Add. info' '''                
        pass

    def load_tab_analysis(self):
        ''' Load data from tab 'Analysis' '''          
        pass
                
    def load_tab_document(self):
        ''' Load data from tab 'Document' '''   
        pass
                
    def load_tab_picture(self):
        ''' Load data from tab 'Document' '''   
        pass
                
    def load_tab_event(self):
        ''' Load data from tab 'Event' '''   
        pass
                
    def load_tab_log(self):
        ''' Load data from tab 'Log' '''   
        pass
        
    def load_tab_rtc(self):
        ''' Load data from tab 'RTC' '''   
        pass
    
    def load_data(self):
        ''' Load data from related tables '''
        
        self.load_tab_add_info()
        self.load_tab_analysis()
        self.load_tab_document()
        self.load_tab_picture()
        self.load_tab_event()
        self.load_tab_log()
        self.load_tab_rtc()
        

    def save_tab_add_info(self):
        ''' Save tab from tab 'Add. info' '''                
        pass

    def save_tab_analysis(self):
        ''' Save tab from tab 'Analysis' '''          
        pass
                
    def save_tab_document(self):
        ''' Save tab from tab 'Document' '''   
        pass
                
    def save_tab_picture(self):
        ''' Save tab from tab 'Document' '''   
        pass
                
    def save_tab_event(self):
        ''' Save tab from tab 'Event' '''   
        pass
                
    def save_tab_log(self):
        ''' Save tab from tab 'Log' '''   
        pass
        
    def save_tab_rtc(self):
        ''' Save tab from tab 'RTC' '''   
        pass
        
                        
    def save_data(self):
        ''' Save data from related tables '''        
        self.save_tab_add_info()
        self.save_tab_analysis()
        self.save_tab_document()
        self.save_tab_picture()
        self.save_tab_event()
        self.save_tab_log()
        self.save_tab_rtc()       
                
        
        
    ''' Slot functions '''           
               
    def save(self):
        ''' Save feature '''
        self.save_data()   
        self.dialog.accept()
        self.close()     
        
        
    def close(self):
        ''' Close form without saving '''
        self.dialog.parent().setVisible(False)         
        
        
    def set_model_to_table(self, widget, table_name, filter_): 
        ''' Set a model with selected filter.
        Attach that model to selected table '''
        
        # Set model
        model = QSqlTableModel();
        model.setTable(table_name)
        model.setEditStrategy(QSqlTableModel.OnManualSubmit)        
        model.setFilter(filter_)
        model.select()         

        # Check for errors
        if model.lastError().isValid():
            self.controller.show_warning(model.lastError().text())      

        # Attach model to table view
        widget.setModel(model)    
        
        
    def delete_records(self, widget, table_name):
        ''' Delete selected elements of the table '''
        
        # Get selected rows
        selected_list = widget.selectionModel().selectedRows()    
        if len(selected_list) == 0:
            message = "Any record selected"
            self.controller.show_warning(message, context_name='ui_message' ) 
            return
        
        inf_text = ""
        list_id = ""
        for i in range(0, len(selected_list)):
            row = selected_list[i].row()
            id_ = widget.model().record(row).value("id")
            inf_text+= str(id_)+", "
            list_id = list_id+"'"+str(id_)+"', "
        inf_text = inf_text[:-2]
        list_id = list_id[:-2]
        answer = self.controller.ask_question("Are you sure you want to delete these records?", "Delete records", inf_text)
        if answer:
            sql = "DELETE FROM "+self.schema_name+"."+table_name 
            sql+= " WHERE id IN ("+list_id+")"
            self.dao.execute_sql(sql)
            widget.model().select()
            
            
    def insert_records (self):
        ''' Insert value  Hydrometer | Hydrometer'''
        
        # Create the dialog and signals
        self.dlg_sum = Add_sum()
        utils_giswater.setDialog(self.dlg_sum)
        # Set signals
        self.dlg_sum.findChild(QPushButton, "btn_accept").clicked.connect(self.btn_accept)
        self.dlg_sum.findChild(QPushButton, "btn_close").clicked.connect(self.btn_close)
        
        # Open the dialog
        self.dlg_sum.exec_() 
        
        
    def btn_accept(self):
        ''' Save new value oh hydrometer'''
        
        # Get widget text - hydtometer_id
        widget_hydro = self.dlg_sum.findChild(QLineEdit, "hydrometer_id_new")          
        self.hydro_id = widget_hydro.text()
        
        # get connec_id       
        widget_connec = self.dialog.findChild(QLineEdit, "connec_id")          
        self.connec_id = widget_connec.text()

        # Insert hydrometer_id in v_rtc_hydrometer
        sql = "INSERT INTO "+self.schema_name+".v_rtc_hydrometer (hydrometer_id) "
        sql+= " VALUES ('"+self.hydro_id+"')"
        self.dao.execute_sql(sql) 
        
        # insert hydtometer_id and connec_id in rtc_hydrometer_x_connec
        sql = "INSERT INTO "+self.schema_name+".v_edit_rtc_hydro_data_x_connec (hydrometer_id, connec_id) "
        sql+= " VALUES ('"+self.hydro_id+"','"+self.connec_id+"')"
        self.dao.execute_sql(sql) 
        
        # Refresh table in Qtableview
        # Fill tab Hydrometer
        table_hydrometer = "v_rtc_hydrometer"
        self.fill_tbl_hydrometer(self.tbl_hydrometer, self.schema_name+"."+table_hydrometer, self.filter)
        
        self.dlg_sum.close()
              
              
    def btn_close(self):
        ''' Close form without saving '''
        self.dlg_sum.close()
       
        
        
    def open_selected_document(self):
        ''' Get value from selected cell ("PATH")
        Open the document ''' 
        
        # Check if clicked value is from the column "PATH"
        position_column = self.tbl_document.currentIndex().column()
        if position_column == 4:      
            # Get data from address in memory (pointer)
            self.path = self.tbl_document.selectedIndexes()[0].data()
            # Check if file exist
            if not os.path.exists(self.path):
                message = "File not found!"
                self.controller.show_warning(message, context_name='ui_message')
               
            else:
                # Open the document
                os.startfile(self.path)                      


    def set_filter_table(self, widget):
        ''' Get values selected by the user and sets a new filter for its table model '''
        
        # Get selected dates
        date_from = self.date_document_from.date().toString('yyyyMMdd') 
        date_to = self.date_document_to.date().toString('yyyyMMdd') 
        if (date_from > date_to):
            message = "Selected date interval is not valid"
            self.controller.show_warning(message, context_name='ui_message')                   
            return
        
        # Set filter
        expr = self.field_id+" = '"+self.id+"'"
        expr+= " AND date >= '"+date_from+"' AND date <= '"+date_to+"'"
        
        # Get selected values in Comboboxes        
        doc_type_value = utils_giswater.getWidgetText("doc_type")
        if doc_type_value != 'null': 
            expr+= " AND doc_type = '"+doc_type_value+"'"
        doc_tag_value = utils_giswater.getWidgetText("doc_tag")
        if doc_tag_value != 'null': 
            expr+= " AND tagcat_id = '"+doc_tag_value+"'"
        doc_user_value = utils_giswater.getWidgetText("doc_user")
        if doc_user_value != 'null':
            expr+= " AND user_name = '"+doc_user_value+"'"
  
        # Refresh model with selected filter
        widget.model().setFilter(expr)
        widget.model().select() 
        
        
    def set_filter_table_man(self, widget):
        ''' Get values selected by the user and sets a new filter for its table model '''
        
        # Get selected dates
        date_from = self.date_document_from.date().toString('yyyyMMdd') 
        date_to = self.date_document_to.date().toString('yyyyMMdd') 
        if (date_from > date_to):
            message = "Selected date interval is not valid"
            self.controller.show_warning(message, context_name='ui_message')                   
            return
        
        # Set filter
        expr = self.field_id+" = '"+self.id+"'"
        expr+= " AND date >= '"+date_from+"' AND date <= '"+date_to+"'"
        
        # Get selected values in Comboboxes        
        doc_type_value = utils_giswater.getWidgetText("doc_type")
        if doc_type_value != 'null': 
            expr+= " AND doc_type = '"+doc_type_value+"'"
        doc_tag_value = utils_giswater.getWidgetText("doc_tag")
        if doc_tag_value != 'null': 
            expr+= " AND tagcat_id = '"+doc_tag_value+"'"
  
        # Refresh model with selected filter
        widget.model().setFilter(expr)
        widget.model().select()  
        
        
    def set_configuration(self, widget, table_name):
        ''' Configuration of tables 
        Set visibility of columns
        Set width of columns '''
        
        widget = utils_giswater.getWidget(widget)
        if not widget:
            return        
        
        # Set width and alias of visible columns
        columns_to_delete = []
        sql = "SELECT column_index, width, alias, status"
        sql+= " FROM "+self.schema_name+".config_ui_forms"
        sql+= " WHERE ui_table = '"+table_name+"'"
        sql+= " ORDER BY column_index"
        rows = self.controller.get_rows(sql)
        if rows:
            for row in rows:        
                if not row['status']:
                    columns_to_delete.append(row['column_index']-1)
                else:
                    width = row['width']
                    if width is None:
                        width = 100
                    widget.setColumnWidth(row['column_index']-1, width)
                    widget.model().setHeaderData(row['column_index']-1, Qt.Horizontal, row['alias'])
        
        # Set order
        widget.model().setSort(0, Qt.AscendingOrder)    
        widget.model().select()
        
        # Delete columns        
        for column in columns_to_delete:
            widget.hideColumn(column) 


    def fill_tbl_document(self, widget, table_name, filter_):
        ''' Fill the table control to show documents'''
        
        
        # Get widgets
        doc_user = self.dialog.findChild(QComboBox, "doc_user")
        doc_type = self.dialog.findChild(QComboBox, "doc_type")
        doc_tag = self.dialog.findChild(QComboBox, "doc_tag")
        self.date_document_to = self.dialog.findChild(QDateEdit, "date_document_to")
        self.date_document_from = self.dialog.findChild(QDateEdit, "date_document_from")

        # Set signals
        doc_user.activated.connect(partial(self.set_filter_table, widget))
        doc_type.activated.connect(partial(self.set_filter_table, widget))
        doc_tag.activated.connect(partial(self.set_filter_table, widget))
        self.date_document_to.dateChanged.connect(partial(self.set_filter_table, widget))
        self.date_document_from.dateChanged.connect(partial(self.set_filter_table, widget))
        self.tbl_document.doubleClicked.connect(self.open_selected_document)

        # Fill ComboBox tagcat_id
        sql = "SELECT DISTINCT(tagcat_id)"
        sql+= " FROM "+table_name
        sql+= " ORDER BY tagcat_id"
        rows = self.dao.get_rows(sql)
        utils_giswater.fillComboBox("doc_tag", rows)

        # Fill ComboBox doccat_id
        sql = "SELECT DISTINCT(doc_type)"
        sql+= " FROM "+table_name
        sql+= " ORDER BY doc_type"
        rows = self.dao.get_rows(sql)
        utils_giswater.fillComboBox("doc_type", rows)

        # Fill ComboBox doc_user
        sql = "SELECT DISTINCT(user_name)"
        sql+= " FROM "+table_name
        sql+= " ORDER BY user_name"
        rows = self.dao.get_rows(sql)
        utils_giswater.fillComboBox("doc_user", rows)
        
        # Set model of selected widget
        self.set_model_to_table(widget, table_name, filter_)
        
        
        
    def fill_tbl_document_man(self, widget, table_name, filter_):
        ''' Fill the table control to show documents'''
        
        # Get widgets  
        doc_type = self.dialog.findChild(QComboBox, "doc_type")
        doc_tag = self.dialog.findChild(QComboBox, "doc_tag")
        self.date_document_to = self.dialog.findChild(QDateEdit, "date_document_to")
        self.date_document_from = self.dialog.findChild(QDateEdit, "date_document_from")

        # Set signals
        doc_type.activated.connect(partial(self.set_filter_table_man, widget))
        doc_tag.activated.connect(partial(self.set_filter_table_man, widget))
        self.date_document_to.dateChanged.connect(partial(self.set_filter_table_man, widget))
        self.date_document_from.dateChanged.connect(partial(self.set_filter_table_man, widget))
        #self.tbl_document.doubleClicked.connect(self.open_selected_document)

        # Fill ComboBox tagcat_id
        sql = "SELECT DISTINCT(tagcat_id)"
        sql+= " FROM "+table_name
        sql+= " ORDER BY tagcat_id"
        rows = self.dao.get_rows(sql)
        utils_giswater.fillComboBox("doc_tag", rows)

        # Fill ComboBox doccat_id
        sql = "SELECT DISTINCT(doc_type)"
        sql+= " FROM "+table_name
        sql+= " ORDER BY doc_type"
        rows = self.dao.get_rows(sql)
        utils_giswater.fillComboBox("doc_type", rows)

        # Set model of selected widget
        self.set_model_to_table(widget, table_name, filter_)
    

    def fill_table(self, widget, table_name, filter_): 
        ''' Fill info tab of node '''
        self.set_model_to_table(widget, table_name, filter_)          
        
        
    def fill_tbl_event(self, widget, table_name, filter_):
        ''' Fill the table control to show documents'''
        
        # Get widgets  
        event_type = self.dialog.findChild(QComboBox, "event_type")
        event_id = self.dialog.findChild(QComboBox, "event_id")
        self.date_event_to = self.dialog.findChild(QDateEdit, "date_event_to")
        self.date_event_from = self.dialog.findChild(QDateEdit, "date_event_from")


        # Set signals
        event_type.activated.connect(partial(self.set_filter_table_event, widget))
        event_id.activated.connect(partial(self.set_filter_table_event, widget))
        self.date_event_to.dateChanged.connect(partial(self.set_filter_table_event, widget))
        self.date_event_from.dateChanged.connect(partial(self.set_filter_table_event, widget))
    

        # Fill ComboBox event_id
        sql = "SELECT DISTINCT(event_id)"
        sql+= " FROM "+table_name
        sql+= " ORDER BY event_id"
        rows = self.dao.get_rows(sql)
        utils_giswater.fillComboBox("event_id", rows)

        # Fill ComboBox event_type
        sql = "SELECT DISTINCT(event_type)"
        sql+= " FROM "+table_name
        sql+= " ORDER BY event_type"
        rows = self.dao.get_rows(sql)
        utils_giswater.fillComboBox("event_type", rows)

        # Set model of selected widget
        self.set_model_to_table(widget, table_name, filter_)    
        
                 
    
    def set_filter_table_event(self, widget):
        ''' Get values selected by the user and sets a new filter for its table model '''
        # Get selected dates
        date_from = self.date_event_from.date().toString('yyyyMMdd') 
        date_to = self.date_event_to.date().toString('yyyyMMdd') 
        if (date_from > date_to):
            message = "Selected date interval is not valid"
            self.controller.show_warning(message, context_name='ui_message')                   
            return
        
        # Set filter
        expr = self.field_id+" = '"+self.id+"'"
        expr+= " AND date >= '"+date_from+"' AND date <= '"+date_to+"'"
        
        # Get selected values in Comboboxes        
        event_type_value = utils_giswater.getWidgetText("event_type")
        if event_type_value != 'null': 
            expr+= " AND event_type = '"+event_type_value+"'"
        event_id_value = utils_giswater.getWidgetText("event_id")
        if event_id_value != 'null': 
            expr+= " AND event_id = '"+event_id_value+"'"
  
        # Refresh model with selected filter
        widget.model().setFilter(expr)
        widget.model().select()  
        

        
    def fill_tbl_hydrometer(self, widget, table_name, filter_):
        ''' Fill the table control to show documents'''
        
        # Get widgets  
        self.date_el_to = self.dialog.findChild(QDateEdit, "date_el_to")
        self.date_el_from = self.dialog.findChild(QDateEdit, "date_el_from")

        # Set signals
        self.date_el_to.dateChanged.connect(partial(self.set_filter_hydrometer, widget))
        self.date_el_from.dateChanged.connect(partial(self.set_filter_hydrometer, widget))
        self.tbl_document.doubleClicked.connect(self.open_selected_document)

        # Set model of selected widget
        self.set_model_to_table(widget, table_name, filter_)
        
        
    def set_filter_hydrometer(self, widget):
        ''' Get values selected by the user and sets a new filter for its table model '''

        
        # Get selected dates
        date_from = self.date_el_from.date().toString('yyyyMMdd') 
        date_to = self.date_el_to.date().toString('yyyyMMdd') 
        if (date_from > date_to):
            message = "Selected date interval is not valid"
            self.controller.show_warning(message, context_name='ui_message')                   
            return
        
        # Set filter
        expr = self.field_id+" = '"+self.id+"'"
        expr+= " AND date >= '"+date_from+"' AND date <= '"+date_to+"'"
  
        # Refresh model with selected filter
        widget.model().setFilter(expr)
        widget.model().select() 
        
        
    def set_tabs_visibility(self):
        ''' Hide some tabs '''     
        
        # Get schema and table name of selected layer       
        (uri_schema, uri_table) = self.controller.get_layer_source(self.layer)   #@UnusedVariable
        if uri_table is None:
            self.controller.show_warning("Error getting table name from selected layer")
            return
        
        if uri_table == self.table_wjoin :
            self.tab_main.removeTab(3)
            self.tab_main.removeTab(2)
            self.tab_main.removeTab(1)
        
        if uri_table == self.table_tap :
            self.tab_main.removeTab(3)
            self.tab_main.removeTab(2)
            self.tab_main.removeTab(0)

        if uri_table == self.table_greentap :
            self.tab_main.removeTab(3)
            self.tab_main.removeTab(1)
            self.tab_main.removeTab(0)

        if uri_table == self.table_fountain :
            self.tab_main.removeTab(2)
            self.tab_main.removeTab(1)
            self.tab_main.removeTab(0) 
            
           
        
        if uri_table == self.table_tank :
            for i in xrange(13,-1,-1):
                if (i != 11) & (i != 10) & (i != 0):
                    self.tab_main.removeTab(i) 
        if uri_table == self.table_pump :
            for i in xrange(13,-1,-1):
                if (i != 11) & (i != 10) & (i != 1):
                    self.tab_main.removeTab(i) 
        if uri_table == self.table_source :
            for i in xrange(13,-1,-1):
                if (i != 11) & (i != 10) & (i != 2):
                    self.tab_main.removeTab(i) 
        if uri_table == self.table_meter :
            for i in xrange(13,-1,-1):
                if (i != 11) & (i != 10) & (i != 3):
                    self.tab_main.removeTab(i) 
        if uri_table == self.table_junction :
            for i in xrange(13,-1,-1):
                if (i != 11) & (i != 10) & (i != 4):
                    self.tab_main.removeTab(i) 
        if uri_table == self.table_waterwell :
            for i in xrange(13,-1,-1):
                if (i != 11) & (i != 10) & (i != 5):
                    self.tab_main.removeTab(i) 
                    
        if uri_table == self.table_reduction :
            for i in xrange(13,-1,-1):
                if (i != 11) & (i != 10) & (i != 6):
                    self.tab_main.removeTab(i) 
        if uri_table == self.table_hydrant :
            for i in xrange(13,-1,-1):
                if (i != 11) & (i != 10) & (i != 7):
                    self.tab_main.removeTab(i) 
        if uri_table == self.table_valve :
            for i in xrange(13,-1,-1):
                if (i != 11) & (i != 10) & (i != 8):
                    self.tab_main.removeTab(i) 
        if uri_table == self.table_manhole :
            for i in xrange(13,-1,-1):
                if (i != 11) & (i != 10) & (i != 5):
                    self.tab_main.removeTab(i) 
        