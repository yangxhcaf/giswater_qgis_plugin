"""
This file is part of Giswater 2.0
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: latin-1 -*-
import re

try:
    from qgis.core import Qgis
except ImportError:
    from qgis.core import QGis as Qgis

if Qgis.QGIS_VERSION_INT < 29900:
    pass
else:
    from builtins import range

from qgis.core import QgsComposerMap, QgsPoint, QgsGeometry, QgsRectangle
from qgis.gui import QgsVertexMarker, QgsRubberBand


from qgis.PyQt.QtCore import Qt, QRectF, QPointF
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QMessageBox


import json
import utils_giswater

from collections import OrderedDict
from functools import partial

from giswater.actions.api_parent import ApiParent
from giswater.ui_manager import ApiComposerUi


class ApiManageComposer(ApiParent):
    def __init__(self, iface, settings, controller, plugin_dir):
        """ Class to control Composer button """
        ApiParent.__init__(self, iface, settings, controller, plugin_dir)

        self.destroyed = False

    def composer(self):
        self.my_json = {}
        self.dlg_composer = ApiComposerUi()
        self.load_settings(self.dlg_composer)

        # Create and populate dialog
        composers_list = self.get_composer()
        extras = '"composers":' + str(composers_list)
        body = self.create_body(extras=extras)
        sql = ("SELECT " + self.schema_name + ".gw_api_getprint($${" + body + "}$$)::text")
        row = self.controller.get_row(sql, log_sql=True)
        if not row:
            self.controller.show_warning("NOT ROW FOR: " + sql)
            return False
        complet_result = [json.loads(row[0], object_pairs_hook=OrderedDict)]
        if complet_result[0]['formTabs']:
            fields = complet_result[0]['formTabs'][0]
            self.create_dialog(self.dlg_composer, fields)



        #self.dlg_composer.cmb_composers.currentIndexChanged.connect(self.selectComposer)
        
        self.dlg_composer.btn_export.clicked.connect(partial(self.accept, self.dlg_composer, self.my_json))
        self.dlg_composer.btn_close.clicked.connect(partial(self.close_dialog, self.dlg_composer))
        self.dlg_composer.btn_close.clicked.connect(self.destructor)
        self.dlg_composer.rejected.connect(self.destructor)
        self.dlg_composer.show()
        # self.iface.composerAdded.connect(lambda view: self.populate_cmb_composer())
        # self.iface.composerWillBeRemoved.connect(self.populate_cmb_composer)
        self.iface.mapCanvas().extentsChanged.connect(partial(self.accept, self.dlg_composer, self.my_json))



    def destructor(self):
        self.destroyed = True
        if self.rubber_polygon:
            self.iface.mapCanvas().scene().removeItem(self.rubber_polygon)
            self.rubber_polygon = None


    def get_composer(self, removed=None):
        """ Get all composers from current QGis project """
        composers = '"{'

        for composer in self.iface.activeComposers():
            if composer != removed and composer.composerWindow():
                cur = composer.composerWindow().windowTitle()
                composers += cur + ', '
        if len(composers) > 1:
            composers = composers[:-2] + '}"'
        else:
            composers += '}"'
        return composers


    def create_dialog(self, dialog, fields):
        for field in fields['fields']:
            label, widget = self.set_widgets(dialog, field)
            self.put_widgets(dialog, field, label, widget)
            self.get_values(dialog, widget, self.my_json)


    def update_rectangle(self, dialog, my_json):
        pass

    def gw_api_setprint(self, dialog, widget, my_json):
        self.accept(dialog, my_json)

    def accept(self, dialog, my_json):
        if self.destroyed:
            return
        if my_json == '' or str(my_json) == '{}':
            self.close_dialog(dialog)
            return
        composer_templates = []
        for composer in self.iface.activeComposers():
            composer_map = []
            composer_template = {'ComposerTemplate': composer.composerWindow().windowTitle()}
            # Get map(item) from each composer template
            index = 0
            for item in composer.composition().items():
                cur_map = {}
                if isinstance(item, QgsComposerMap):
                    cur_map['width'] = item.rect().width()
                    cur_map['height'] = item.rect().height()
                    cur_map['name'] = item.displayName()
                    cur_map['index'] = index
                    composer_map.append(cur_map)
                    composer_template['ComposerMap'] = composer_map
                    index += 1
            composer_templates.append(composer_template)
            my_json['ComposerTemplates'] = composer_templates

        composer_name = my_json['composer']
        rotation = my_json['rotation']
        scale = my_json['scale']
        extent = self.iface.mapCanvas().extent()

        p1 = {'xcoord': extent.xMinimum(), 'ycoord': extent.yMinimum()}
        p2 = {'xcoord': extent.xMaximum(), 'ycoord': extent.yMaximum()}
        ext = {'p1': p1, 'p2': p2}
        my_json['extent'] = ext

        my_json = json.dumps(my_json)
        client = '"client":{"device":9, "infoType":100, "lang":"ES"}, '
        form = '"form":{''}, '
        feature = '"feature":{''}, '
        data = '"data":' + str(my_json)
        body = "" + client + form + feature + data
        sql = ("SELECT " + self.schema_name + ".gw_api_setprint($${" + body + "}$$)::text")
        row = self.controller.get_row(sql, log_sql=True)
        complet_result = [json.loads(row[0], object_pairs_hook=OrderedDict)]
        result = complet_result[0]['data']
        self.draw_rectangle(result)
        map_index = complet_result[0]['data']['mapIndex']

        maps = []
        for composer in self.iface.activeComposers():
            maps = []
            if composer.composerWindow().windowTitle() == composer_name:
                for item in composer.composition().items():
                    if isinstance(item, QgsComposerMap):
                        maps.append(item)
                break
        if len(maps) > 0:
            self.iface.mapCanvas().setRotation(float(rotation))
            maps[map_index].zoomToExtent(self.iface.mapCanvas().extent())
            maps[map_index].setNewScale(float(scale))
            maps[map_index].setMapRotation(float(rotation))

