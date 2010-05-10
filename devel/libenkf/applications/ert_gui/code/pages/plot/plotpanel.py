from PyQt4 import QtGui, QtCore
from pages.config.parameters.parameterpanel import Parameter
from pages.plot.plotview import PlotView
import ertwrapper
import pages.config.parameters.parameterpanel
import widgets.helpedwidget
from widgets.helpedwidget import ContentModel
from pages.config.parameters.parametermodels import DataModel, FieldModel, KeywordModel, SummaryModel
from pages.plot.plotdata import PlotContextDataFetcher, PlotDataFetcher, enums

class PlotPanel(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        plotLayout = QtGui.QHBoxLayout()

        self.plot = PlotView()

        parameterLayout = QtGui.QVBoxLayout()
        self.plotList = QtGui.QListWidget(self)
        self.plotList.setMaximumWidth(150)
        self.plotList.setMinimumWidth(150)

        self.plotDataPanel = PlotParameterPanel(self, 150)
        self.connect(self.plotDataPanel.keyIndexCombo, QtCore.SIGNAL('currentIndexChanged(QString)'), self.keyIndexChanged)
        self.connect(self.plotDataPanel.stateCombo, QtCore.SIGNAL('currentIndexChanged(QString)'), self.stateChanged)
        self.connect(self.plotDataPanel.keyIndexI, QtCore.SIGNAL('valueChanged(int)'), lambda i : self.fieldPositionChanged(self.plotDataPanel.getFieldPosition()))
        self.connect(self.plotDataPanel.keyIndexJ, QtCore.SIGNAL('valueChanged(int)'), lambda i : self.fieldPositionChanged(self.plotDataPanel.getFieldPosition()))
        self.connect(self.plotDataPanel.keyIndexK, QtCore.SIGNAL('valueChanged(int)'), lambda i : self.fieldPositionChanged(self.plotDataPanel.getFieldPosition()))
        parameterLayout.addWidget(self.plotList)
        parameterLayout.addWidget(self.plotDataPanel)

        self.connect(self.plotList, QtCore.SIGNAL('currentItemChanged(QListWidgetItem *, QListWidgetItem *)'), self.select)
        ContentModel.modelConnect('initialized()', self.updateList)
        #todo: listen to ensemble changes!


        self.plotDataFetcher = PlotDataFetcher()
        self.plotContextDataFetcher = PlotContextDataFetcher()


        plotLayout.addLayout(parameterLayout)
        plotLayout.addWidget(self.plot)
        self.plotViewSettings = PlotViewSettingsPanel(plotView=self.plot, width=150)
        plotLayout.addWidget(self.plotViewSettings)
        self.setLayout(plotLayout)


    def drawPlot(self):
        self.plot.setData(self.plotDataFetcher.data)
        self.plot.drawPlot()

    def select(self, current, previous):
        self.plotDataFetcher.setParameter(current)
        self.plotDataFetcher.setState(self.plotDataPanel.getState())
        self.plotDataFetcher.fetchContent()

        self.plotDataPanel.activatePanel(current.getType().name)

        if current.getType() == KeywordModel.TYPE:
            self.disconnect(self.plotDataPanel.keyIndexCombo, QtCore.SIGNAL('currentIndexChanged(QString)'), self.keyIndexChanged)
            self.plotDataPanel.keyIndexCombo.clear()
            self.plotDataPanel.keyIndexCombo.addItems(self.plotContextDataFetcher.data.getKeyIndexList(current.getName()))
            self.connect(self.plotDataPanel.keyIndexCombo, QtCore.SIGNAL('currentIndexChanged(QString)'), self.keyIndexChanged)
        elif current.getType() == FieldModel.TYPE:
            #self.plotDataPanel.setFieldBounds()
            pass

        self.drawPlot()

    def updateList(self):
        self.plotContextDataFetcher.fetchContent()
        self.plotList.clear()
        for parameter in self.plotContextDataFetcher.data.parameters:
            self.plotList.addItem(parameter)

        self.plotList.sortItems()

        self.plotViewSettings.setDefaultErrorbarMaxValue(self.plotContextDataFetcher.data.errorbar_max)

    def stateChanged(self):
        self.plotDataFetcher.setState(self.plotDataPanel.getState())
        self.plotDataFetcher.fetchContent()
        self.drawPlot()

    def fieldPositionChanged(self, position):
        parameter = self.plotDataFetcher.getParameter()
        pos = "%i,%i,%i" % (position[0], position[1], position[2])
        parameter.setData(pos)
        self.plotDataFetcher.setState(self.plotDataPanel.getState())
        self.plotDataFetcher.fetchContent()
        self.drawPlot()

    def keyIndexChanged(self, key):
        parameter = self.plotDataFetcher.getParameter()
        parameter.setData(str(key))
        self.plotDataFetcher.setState(self.plotDataPanel.getState())
        self.plotDataFetcher.fetchContent()
        self.drawPlot()


class PlotViewSettingsPanel(QtGui.QFrame):
    def __init__(self, parent=None, plotView=None, width=100):
        QtGui.QFrame.__init__(self, parent)
        self.setFrameShape(QtGui.QFrame.StyledPanel)
        self.setFrameShadow(QtGui.QFrame.Plain)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self.setMinimumWidth(width)
        self.setMaximumWidth(width)

        self.plotView = plotView

        layout = QtGui.QFormLayout()
        layout.setRowWrapPolicy(QtGui.QFormLayout.WrapLongRows)

        self.showErrorbarChk = QtGui.QCheckBox("")
        self.showErrorbarChk.setChecked(plotView.getShowErrorbar())
        self.connect(self.showErrorbarChk, QtCore.SIGNAL("stateChanged(int)"), lambda state : self.plotView.showErrorbar(state == QtCore.Qt.Checked))
        layout.addRow("Show errorbars", self.showErrorbarChk)


        self.errorbarModes = QtGui.QComboBox()
        errorbarItems = ["Auto", "Errorbar", "Errorline"]
        self.errorbarModes.addItems(errorbarItems)
        self.errorbar_max = -1
        def errorbar(index):
            if index == 0: #auto
                self.plotView.setErrorbarLimit(self.errorbar_max)
            elif index == 1: #only show show errorbars
                self.plotView.setErrorbarLimit(10000)
            else: #only show error lines
                self.plotView.setErrorbarLimit(0)


        self.connect(self.errorbarModes, QtCore.SIGNAL("currentIndexChanged(int)"), errorbar)
        layout.addRow("Errorbar", self.errorbarModes)


        self.alphaSpn = QtGui.QDoubleSpinBox(self)
        self.alphaSpn.setMinimum(0.0)
        self.alphaSpn.setMaximum(1.0)
        self.alphaSpn.setDecimals(3)
        self.alphaSpn.setSingleStep(0.01)
        self.alphaSpn.setValue(plotView.getAlphaValue())
        self.connect(self.alphaSpn, QtCore.SIGNAL('valueChanged(double)'), self.plotView.setAlphaValue)
        layout.addRow("Blend factor", self.alphaSpn)


        self.setLayout(layout)

    def setDefaultErrorbarMaxValue(self, errorbar_max):
        self.errorbar_max = errorbar_max
        if self.errorbarModes.currentIndex == 0: #auto
            self.plotView.setErrorbarLimit(errorbar_max)


class PlotParameterPanel(QtGui.QFrame):

    def __init__(self, parent=None, width=100):
        QtGui.QFrame.__init__(self, parent)
        self.setFrameShape(QtGui.QFrame.StyledPanel)
        self.setFrameShadow(QtGui.QFrame.Plain)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self.setMinimumWidth(width)
        self.setMaximumWidth(width)
        self.setMaximumHeight(200)

        self.stack = QtGui.QStackedWidget()

        self.summaryPanel = self.createSummaryPanel()
        self.keywordPanel = self.createKeywordPanel()
        self.fieldPanel = self.createFieldPanel()

        self.stack.addWidget(self.summaryPanel)
        self.stack.addWidget(self.keywordPanel)
        self.stack.addWidget(self.fieldPanel)

        comboLayout, self.stateCombo = self.createStateCombo()

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.stack)
        layout.addStretch()
        layout.addLayout(comboLayout)
        self.setLayout(layout)

    def activatePanel(self, parameter_type_name):
        if parameter_type_name == SummaryModel.TYPE.name:
            self.stack.setCurrentWidget(self.summaryPanel)
        elif parameter_type_name == KeywordModel.TYPE.name:
            self.stack.setCurrentWidget(self.keywordPanel)
        elif parameter_type_name == FieldModel.TYPE.name:
            self.stack.setCurrentWidget(self.fieldPanel)
        else:
            print "Unknown parametertype"

    def createStateCombo(self):
        layout = QtGui.QFormLayout()
        layout.setRowWrapPolicy(QtGui.QFormLayout.WrapLongRows)

        stateCombo = QtGui.QComboBox()

        for state in enums.ert_state_enum.values():
            stateCombo.addItem(state.name)
            
        stateCombo.setCurrentIndex(0)

        layout.addRow("State:", stateCombo)
        return layout, stateCombo

    def createSummaryPanel(self):
        panel = QtGui.QFrame()
        panel.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        return panel

    def createKeywordPanel(self):
        widget = QtGui.QWidget()
        layout = QtGui.QFormLayout()
        layout.setMargin(0)
        layout.setRowWrapPolicy(QtGui.QFormLayout.WrapLongRows)
        self.keyIndexCombo = QtGui.QComboBox()
        layout.addRow("Key index:", self.keyIndexCombo)
        widget.setLayout(layout)
        return widget

    def createFieldPanel(self):
        widget = QtGui.QWidget()
        layout = QtGui.QFormLayout()
        layout.setMargin(0)
        layout.setRowWrapPolicy(QtGui.QFormLayout.WrapLongRows)

        self.keyIndexI = QtGui.QSpinBox()
        self.keyIndexI.setMinimum(0)

        layout.addRow("I:", self.keyIndexI)

        self.keyIndexJ = QtGui.QSpinBox()
        self.keyIndexJ.setMinimum(0)
        layout.addRow("J:", self.keyIndexJ)

        self.keyIndexK = QtGui.QSpinBox()
        self.keyIndexK.setMinimum(0)
        layout.addRow("K:", self.keyIndexK)

        self.setFieldBounds(10, 10, 10)

        widget.setLayout(layout)
        return widget

    def setFieldBounds(self, i, j, k):
        self.keyIndexI.setMaximum(i)
        self.keyIndexJ.setMaximum(j)
        self.keyIndexK.setMaximum(k)

    def getFieldPosition(self):
        return (self.keyIndexI.value(), self.keyIndexJ.value(), self.keyIndexK.value())

    def getState(self):
        selectedName = str(self.stateCombo.currentText())
        return enums.ert_state_enum.resolveName(selectedName)
