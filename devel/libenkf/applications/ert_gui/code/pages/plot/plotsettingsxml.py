import xml.dom.minidom
import os

class PlotSettingsSaver:
    def __init__(self):
        pass

    def save(self, name, plot_settings, annotations):
        """Save plot configuration to a file with the specified name as filename."""
        self.doc = xml.dom.minidom.Document()

        self.root_element = self.doc.createElement("plot_configuration")
        self.root_element.setAttribute("name", name)
        self.doc.appendChild(self.root_element)

        plot_configs = plot_settings.getPlotConfigList()

        for plot_config in plot_configs:
            self.__addPlotConfig(plot_config)

        self.__addLimits(plot_settings.getLimitsTuple(), plot_settings.getZoomTuple())
        self.__addSelectedMembers(plot_settings.getSelectedMembers())

        self.__addAnnotations(annotations)

        file_object = open("%s/%s.xml" % (plot_settings.getPlotConfigPath(), name), "w")
        file_object.write(self.doc.toprettyxml())
        file_object.close()

    def __addPlotConfig(self, plot_config):
        """Add a plot config to the xml"""
        pc_element = self.doc.createElement("plot_config")
        self.root_element.appendChild(pc_element)
        pc_element.setAttribute("name", str(plot_config.name))
        pc_element.setAttribute("visible", str(plot_config.is_visible))
        pc_element.setAttribute("z_order", str(plot_config.z_order))
        pc_element.setAttribute("picker", str(plot_config.picker))

        color = plot_config.color
        alpha = plot_config.alpha

        color_element = self.doc.createElement("color")
        pc_element.appendChild(color_element)

        color_element.setAttribute("alpha", str(alpha))
        color_element.setAttribute("red", str(color[0]))
        color_element.setAttribute("green", str(color[1]))
        color_element.setAttribute("blue", str(color[2]))

        style_element = self.doc.createElement("style")
        pc_element.appendChild(style_element)

        style_element.setAttribute("line", str(plot_config.linestyle))
        style_element.setAttribute("marker", str(plot_config.marker))

    def __addComments(self, limits_element):
        comment1 = "When limit values represent a date, the date is stored "\
          "as the number of seconds since 1/1-1970."

        comment2 = "Setting a limit value to None means that the program should "\
          "use the corresponding value from the dataset as limits."

        comment_element = self.doc.createComment(comment1)
        limits_element.appendChild(comment_element)
        comment_element = self.doc.createComment(comment2)
        limits_element.appendChild(comment_element)

    def __addLimits(self, limits, zoom):
        """Add limits and zoom to the xml"""
        element = self.doc.createElement("limits_and_zoom")
        self.root_element.appendChild(element)

        limits_element = self.doc.createElement("limits")

        self.__addComments(limits_element)
        
        element.appendChild(limits_element)
        limits_element.setAttribute("x_min", str(limits[0]))
        limits_element.setAttribute("x_max", str(limits[1]))
        limits_element.setAttribute("y_min", str(limits[2]))
        limits_element.setAttribute("y_max", str(limits[3]))

        zoom_element = self.doc.createElement("zoom")
        element.appendChild(zoom_element)
        zoom_element.setAttribute("x_min", str(zoom[0]))
        zoom_element.setAttribute("x_max", str(zoom[1]))
        zoom_element.setAttribute("y_min", str(zoom[2]))
        zoom_element.setAttribute("y_max", str(zoom[3]))

    def __addSelectedMembers(self, selected_members):
        """Add list of selected members to the xml"""
        element = self.doc.createElement("selected_members")
        self.root_element.appendChild(element)

        for selected_member in selected_members:
            member = self.doc.createElement("member")
            element.appendChild(member)
            member.setAttribute("id", str(selected_member))

    def __addAnnotations(self, annotations):
        """Add list of annotations to the xml"""
        element = self.doc.createElement("annotations")
        self.root_element.appendChild(element)

        for annotation in annotations:
            annotation_element = self.doc.createElement("annotation")
            element.appendChild(annotation_element)
            annotation_element.setAttribute("label", str(annotation[0]))
            annotation_element.setAttribute("x", str(annotation[1]))
            annotation_element.setAttribute("y", str(annotation[2]))
            annotation_element.setAttribute("xt", str(annotation[3]))
            annotation_element.setAttribute("yt", str(annotation[4]))


class PlotSettingsLoader:
    def __init__(self):
        self.annotations = None
        self.skip_plot_settings = False
        self.skip_limits_and_zoom = False
        self.skip_selected_members = False
        self.skip_annotations = False

    def skipPlotSettings(self, bool=True):
        self.skip_plot_settings = bool

    def skipLimitsAndZoom(self, bool=True):
        self.skip_limits_and_zoom = bool

    def skipSelectedMembers(self, bool=True):
        self.skip_selected_members = bool

    def skipAnnotations(self, bool=True):
        self.skip_annotations = bool

    def copy(self, plot_settings):
        pscd = PlotSettingsCopyDialog(plot_settings)
        success = pscd.exec_()
        if success:
            self.skipPlotSettings(not pscd.shouldCopyPlotSettings())
            self.skipLimitsAndZoom(not pscd.shouldCopyRangeLimits())
            self.skipSelectedMembers(not pscd.shouldCopySelectedMembers())
            self.skipAnnotations(not pscd.shouldCopyAnnotations())
            self.load(pscd.getName(), plot_settings)


    def load(self, name, plot_settings):
        filename = "%s/%s.xml" % (plot_settings.getPlotConfigPath(), name)

        if os.path.exists(filename):
            self.doc = xml.dom.minidom.parse(filename)

            if not self.skip_plot_settings:
                self.__loadPlotConfigs(plot_settings)

            if not self.skip_limits_and_zoom:
                self.__loadLimitsAndZoom(plot_settings)

            if not self.skip_selected_members:
                self.__loadSelectedMembers(plot_settings)

            if not self.skip_annotations:
                self.__loadAnnotations(plot_settings)

    def __loadPlotConfigs(self, plot_settings):
        plot_config_dict = plot_settings.getPlotConfigDict()
        xml_plot_configs = self.doc.getElementsByTagName("plot_config")

        for xml_plot_config in xml_plot_configs:
            name = xml_plot_config.getAttribute("name")
            plot_config = plot_config_dict[name]
            block_state = plot_config.signal_handler.blockSignals(True)
            visible = xml_plot_config.getAttribute("visible")
            z_order = xml_plot_config.getAttribute("z_order")
            picker = xml_plot_config.getAttribute("picker")

            plot_config.is_visible = visible.lower() == "true"
            plot_config.z_order = int(z_order)

            if picker.lower() == "none":
                plot_config.picker = None
            else:
                plot_config.picker = int(picker)

            xml_color = xml_plot_config.getElementsByTagName("color")[0]

            a = xml_color.getAttribute("alpha")
            r = xml_color.getAttribute("red")
            g = xml_color.getAttribute("green")
            b = xml_color.getAttribute("blue")

            plot_config.alpha = float(a)
            plot_config.color = (float(r), float(g), float(b))

            xml_style = xml_plot_config.getElementsByTagName("style")[0]

            linestyle = xml_style.getAttribute("line")
            marker = xml_style.getAttribute("marker")

            plot_config.linestyle = linestyle
            plot_config.marker = marker

            plot_config.signal_handler.blockSignals(block_state)


    def floatify(self, f):
        if f.lower() == "none":
            return None
        else:
            return float(f)

    def __loadLimitsAndZoom(self, plot_settings):
        xml_limits_and_zoom = self.doc.getElementsByTagName("limits_and_zoom")[0]

        xml_limits = xml_limits_and_zoom.getElementsByTagName("limits")[0]
        x_min = xml_limits.getAttribute("x_min")
        x_max = xml_limits.getAttribute("x_max")
        y_min = xml_limits.getAttribute("y_min")
        y_max = xml_limits.getAttribute("y_max")

        plot_settings.setMinXLimit(self.floatify(x_min))
        plot_settings.setMaxXLimit(self.floatify(x_max))
        plot_settings.setMinYLimit(self.floatify(y_min))
        plot_settings.setMaxYLimit(self.floatify(y_max))

        xml_zoom = xml_limits_and_zoom.getElementsByTagName("zoom")[0]

        x_min = xml_zoom.getAttribute("x_min")
        x_max = xml_zoom.getAttribute("x_max")
        y_min = xml_zoom.getAttribute("y_min")
        y_max = xml_zoom.getAttribute("y_max")

        plot_settings.setMinXZoom(self.floatify(x_min))
        plot_settings.setMaxXZoom(self.floatify(x_max))
        plot_settings.setMinYZoom(self.floatify(y_min))
        plot_settings.setMaxYZoom(self.floatify(y_max))

    def __loadSelectedMembers(self, plot_settings):
        xml_selected_members = self.doc.getElementsByTagName("selected_members")[0]

        xml_members = xml_selected_members.getElementsByTagName("member")

        plot_settings.clearMemberSelection()
        for member in xml_members:
            m = member.getAttribute("id")
            plot_settings.selectMember(int(m))

    def __loadAnnotations(self, plot_settings):
        xml_annotations_element = self.doc.getElementsByTagName("annotations")[0]

        xml_annotations = xml_annotations_element.getElementsByTagName("annotation")

        self.annotations = []
        for annotation in xml_annotations:
            label = annotation.getAttribute("label")
            x = annotation.getAttribute("x")
            y = annotation.getAttribute("y")
            xt = annotation.getAttribute("xt")
            yt = annotation.getAttribute("yt")

            self.annotations.append((label, float(x), float(y), float(xt), float(yt)))

    def getAnnotations(self):
        return self.annotations


from PyQt4.QtGui import QDialog, QFormLayout, QLabel, QDialogButtonBox, QComboBox, QCheckBox
from PyQt4.QtCore import Qt, SIGNAL
from widgets.util import createSpace

class PlotSettingsCopyDialog(QDialog):
    def __init__(self, plot_settings, parent = None):
        QDialog.__init__(self, parent)

        self.setModal(True)
        self.setWindowTitle("Copy plot settings")
        self.setMinimumWidth(250)
        self.setMinimumHeight(150)

        layout = QFormLayout()

        self.settings_list = QComboBox()

        files = self.listSettings(plot_settings.plot_config_path)

        for file in files:
            index = file.find(".xml")
            name = file[0:index]
            self.settings_list.addItem(name)

        self.check_plot_settings = QCheckBox()
        self.check_plot_settings.setChecked(True)
        self.check_range_limits = QCheckBox()
        self.check_range_limits.setChecked(True)
        self.check_selected_members = QCheckBox()
        self.check_selected_members.setChecked(True)
        self.check_annotations = QCheckBox()
        self.check_annotations.setChecked(True)

        layout.addRow(createSpace(10))
        layout.addRow("Copy from:", self.settings_list)
        layout.addRow("Plot settings:", self.check_plot_settings)
        layout.addRow("Range limits:", self.check_range_limits)
        layout.addRow("Selected members:", self.check_selected_members)
        layout.addRow("Annotations:", self.check_annotations)

        layout.addRow(createSpace(10))

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)

        layout.addRow(buttons)

        self.connect(buttons, SIGNAL('accepted()'), self.accept)
        self.connect(buttons, SIGNAL('rejected()'), self.reject)

        self.setLayout(layout)

    def getName(self):
        return str(self.settings_list.currentText()).strip()

    def shouldCopyPlotSettings(self):
        return self.check_plot_settings.isChecked()

    def shouldCopyRangeLimits(self):
        return self.check_range_limits.isChecked()

    def shouldCopySelectedMembers(self):
        return self.check_selected_members.isChecked()

    def shouldCopyAnnotations(self):
        return self.check_annotations.isChecked()

    def listSettings(self, path):
        """Returns a list of settings filenames."""
        files = os.listdir(path)
        return sorted(filter(self.xmlFilter, files))

    def xmlFilter(self, file):
        """Filter .xml files from a list of filenames"""
        return file.endswith(".xml")

        
        
        







        

