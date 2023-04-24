import hou, subprocess, tempfile

from PySide2 import QtWidgets, QtCore
from PySide2.QtWidgets import *

temp_folder = tempfile.gettempdir()
temp_folder = temp_folder.replace("\\", "/")

blender_folder = "C:/Program Files/Blender Foundation\Blender 3.5/"
blender_folder = blender_folder.replace("\\", "/")

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()

        # Set the window title
        self.setWindowTitle("to blender")

        # Set the window size
        self.resize(300, 400)
        self.setContentsMargins(5,5,5,5)
                
        # Connect the callback function to the update event loop
        hou.ui.addEventLoopCallback(self.update_selected_nodes)
        
        # Initialize the currently selected node(s)
        self.selected_nodes = hou.selectedNodes()

        # Create a radio button group
        self.radio_group = QtWidgets.QButtonGroup()

        # Create the blender radio button and add it to the group
        self.radio_button_1 = QtWidgets.QRadioButton("USD", self)
        self.radio_group.addButton(self.radio_button_1)
        self.radio_button_1.setChecked(True)
        
        # Create the maya radio button and add it to the group
        self.radio_button_2 = QtWidgets.QRadioButton("FBX", self)
        self.radio_group.addButton(self.radio_button_2)
        
        # Create label of the selected nodes
        self.textedit_nodelist = QtWidgets.QTextEdit(self)
        self.textedit_nodelist.setGeometry(130, 50, 325, 200)
        self.textedit_nodelist.setAlignment(QtCore.Qt.AlignTop)

        if len(self.selected_nodes) > 0:
            selected_node_names = [node.name() + " - " + node.type().name() + "\n" for node in self.selected_nodes]
            self.textedit_nodelist.setText("".join(selected_node_names))
        else:
            self.textedit_nodelist.setText("No nodes selected.")        

        # Create checkbox for custom temp folder
        self.checkbox_custom = QCheckBox('custom temp folder', self)
        self.checkbox_custom.setGeometry(130, 170, 110, 30)
        self.checkbox_custom.setChecked(False)

        # Create checkbox for custom blender location
        self.checkbox_blender = QCheckBox('blender folder', self)
        self.checkbox_blender.setGeometry(130, 170, 110, 30)
        self.checkbox_blender.setChecked(False)
        
        # Create checkbox for animations
        self.checkbox_ani = QCheckBox('include animations (cached)', self)
        self.checkbox_ani.setGeometry(250, 170, 200, 30)
        self.checkbox_ani.setChecked(False)

        # Create a text box for the temp folder
        self.textbox_temp = QtWidgets.QLineEdit(temp_folder, self)
        self.textbox_temp.setAlignment(QtCore.Qt.AlignLeft)
        self.textbox_temp.setEnabled(False)

        # Create a text box for the temp folder
        self.textbox_blender = QtWidgets.QLineEdit(blender_folder, self)
        self.textbox_blender.setAlignment(QtCore.Qt.AlignLeft)
        self.textbox_blender.setEnabled(False)
            
        # Create browse temp folder button
        self.btn_browse_temp = QPushButton('Browse', self)
        self.btn_browse_temp.clicked.connect(self.onBrowseTemp)
        self.btn_browse_temp.setEnabled(False)

        # Create browse blender.exe button
        self.btn_browse_blender = QPushButton('Browse', self)
        self.btn_browse_blender.clicked.connect(self.onBrowseBlender)
        self.btn_browse_blender.setEnabled(False)
     
        # Create a ok button
        self.btn_ok = QtWidgets.QPushButton("OK", self)
        self.btn_ok.setGeometry(130, 250, 50, 30)
        self.btn_ok.clicked.connect(self.on_ok_button_clicked)
        self.btn_ok.clicked.connect(self.close)
        
        # Create a cancel btn_ok
        self.btn_cancel = QtWidgets.QPushButton("CANCEL", self)
        self.btn_cancel.setGeometry(185, 250, 60, 30)
        self.btn_cancel.clicked.connect(self.close)
                
        # Set the window flags to make the window always on top
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        
        # Set the window flags to remove the help btn_ok
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        # Update custom options checkbox
        self.checkbox_custom.stateChanged.connect(self.customChecked)
        self.checkbox_blender.stateChanged.connect(self.blenderChecked)

        # Create a QTabWidget
        self.tabs = QTabWidget(self)
        self.tabs.setContentsMargins(15,15,15,15)
        self.setCentralWidget(self.tabs)

        # Create the first tab
        self.tab1 = QWidget()
        self.tab1_layout = QVBoxLayout(self.tab1)
        self.tabs.addTab(self.tab1, "export")

        hbox_1_top = QHBoxLayout()
        hbox_1_middle = QHBoxLayout()
        hbox_1_bottom = QHBoxLayout()

        radio_box = QHBoxLayout()
        textedit_nodelist_box = QVBoxLayout()
        checkbox_ani_box = QHBoxLayout()
        buttons_box = QHBoxLayout()

        radio_box.addWidget(self.radio_button_1)
        radio_box.addWidget(self.radio_button_2)
        radio_box.setSpacing(20)
        textedit_nodelist_box.addWidget(self.textedit_nodelist)
        checkbox_ani_box.addWidget(self.checkbox_ani)
        buttons_box.addWidget(self.btn_ok)
        buttons_box.addWidget(self.btn_cancel)

        grp_box_dcc = QtWidgets.QGroupBox("format")
        grp_box_selected = QtWidgets.QGroupBox("selected nodes")
        grp_box_options = QtWidgets.QGroupBox("extra options")

        grp_box_dcc.setLayout(hbox_1_top)
        grp_box_selected.setLayout(hbox_1_middle)
        grp_box_options.setLayout(hbox_1_bottom)
        
        self.tab1_layout.addWidget(grp_box_dcc)
        self.tab1_layout.addWidget(grp_box_selected)
        self.tab1_layout.addWidget(grp_box_options)
        
        self.tab1_layout.addLayout(buttons_box)
        hbox_1_top.addLayout(radio_box)
        hbox_1_top.setAlignment(QtCore.Qt.AlignHCenter)
        hbox_1_middle.addLayout(textedit_nodelist_box)
        hbox_1_bottom.addLayout(checkbox_ani_box)
    
        # Create the second tab
        self.tab2 = QWidget()
        self.tab2_layout = QVBoxLayout(self.tab2)
        self.tabs.addTab(self.tab2, "options")

        hbox_2_top = QHBoxLayout()
        hbox_2_middle = QHBoxLayout()
        hbox_2_bottom = QHBoxLayout()

        vbox1 = QVBoxLayout()
        custom_box = QHBoxLayout()
        tempfolder_box = QHBoxLayout()

        vbox2 = QVBoxLayout()
        maya_box = QHBoxLayout()
        mayafolder_box = QHBoxLayout()

        vbox3 = QVBoxLayout()
        blender_box = QHBoxLayout()
        blenderfolder_box = QHBoxLayout()
        
        custom_box.addWidget(self.checkbox_custom)
        tempfolder_box.addWidget(self.textbox_temp)
        tempfolder_box.addWidget(self.btn_browse_temp)
        vbox1.addLayout(custom_box)
        vbox1.addLayout(tempfolder_box)

        blender_box.addWidget(self.checkbox_blender)
        blenderfolder_box.addWidget(self.textbox_blender)
        blenderfolder_box.addWidget(self.btn_browse_blender)
        vbox2.addLayout(blender_box)
        vbox2.addLayout(blenderfolder_box)

        vbox3.addLayout(maya_box)
        vbox3.addLayout(mayafolder_box)

        grp_box_custom = QtWidgets.QGroupBox("temp folder")
        grp_box_custom.setLayout(hbox_2_top)

        grp_box_blender = QtWidgets.QGroupBox("blender folder")
        grp_box_blender.setLayout(hbox_2_middle)

        grp_box_empty = QtWidgets.QGroupBox("empty")
        grp_box_empty.setLayout(hbox_2_bottom)

        self.tab2_layout.addWidget(grp_box_custom)
        self.tab2_layout.addWidget(grp_box_blender)
        self.tab2_layout.addWidget(grp_box_empty)

        hbox_2_top.addLayout(vbox1)
        hbox_2_top.setAlignment(QtCore.Qt.AlignTop)

        hbox_2_middle.addLayout(vbox2)
        hbox_2_middle.setAlignment(QtCore.Qt.AlignTop)

        hbox_2_bottom.addLayout(vbox3)
        hbox_2_bottom.setAlignment(QtCore.Qt.AlignTop)

        # The tab stylesheet
        self.tabs.setStyleSheet("""
            QTabWidget::pane {border: 1px solid #2a2a2a; border-bottom-left-radius: 4px; border-bottom-right-radius: 4px; border-top-right-radius: 4px; background-color: #4a4a4a;}
            QTabBar::tab {border: 1px solid #2a2a2a; border-top-left-radius: 4px; border-top-right-radius: 4px; min-width: 10ex; padding: 2px; border-bottom: none;}
            QTabBar::tab:selected, QTabBar::tab:hover {background-color: #4a4a4a;}
        """)
        
        # The textbox stylesheet
        self.textedit_nodelist.setStyleSheet("""
            QTextEdit {background: transparent;}
            QScrollBar:vertical {border: none; background-color: transparent; width: 12px; margin: 0px 0px 0px 0px;}
            QScrollBar::handle:vertical {background: #333333; min-height: 20px;}
            QScrollBar::add-line:vertical {border: none; background: none; height: 0px; subcontrol-position: bottom; subcontrol-origin: margin;}
            QScrollBar::sub-line:vertical {border: none; background: none; height: 0px; subcontrol-position: top; subcontrol-origin: margin;}
        """)

        grp_box_dcc.setStyleSheet("""
            QGroupBox {background-color: transparent; border: 1px solid #333333; padding: 16px; border-radius: 3px; margin-top: 0.5em;}
            QGroupBox::title {subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px;}
        """)

        grp_box_selected.setStyleSheet("""
            QGroupBox {background-color: transparent; border: 1px solid #333333; padding: 16px; border-radius: 3px; margin-top: 0.5em;}
            QGroupBox::title {subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px;}
        """)

        grp_box_options.setStyleSheet("""
            QGroupBox {background-color: transparent; border: 1px solid #333333; padding: 16px; border-radius: 3px; margin-top: 0.5em;}
            QGroupBox::title {subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px;}
        """)

        grp_box_custom.setStyleSheet("""
            QGroupBox {background-color: transparent; border: 1px solid #333333; padding: 16px; border-radius: 3px; margin-top: 0.5em;}
            QGroupBox::title {subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px;}
        """)

        grp_box_blender.setStyleSheet("""
            QGroupBox {background-color: transparent; border: 1px solid #333333; padding: 16px; border-radius: 3px; margin-top: 0.5em;}
            QGroupBox::title {subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px;}
        """)

        grp_box_empty.setStyleSheet("""
            QGroupBox {background-color: transparent; border: 1px solid #333333; padding: 16px; border-radius: 3px; margin-top: 0.5em;}
            QGroupBox::title {subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px;}
        """)


    def update_selected_nodes(self):
        # Get the currently selected node(s)
        new_selected_nodes = hou.selectedNodes()
                
        # If the selected node(s) have changed, update the text box
        if self.selected_nodes != new_selected_nodes:
            self.selected_nodes = new_selected_nodes
            
            # If there are no selected nodes, display a message in the text box
            if not self.selected_nodes:
                self.textedit_nodelist.setText("No nodes selected.")
            
            # If there are multiple selected nodes, display a list of their names in the text box
            else:
                selected_node_names = [node.name() + " - " + node.type().name() + "\n" for node in self.selected_nodes]
                self.textedit_nodelist.setText("".join(selected_node_names))
                
                
    def on_ok_button_clicked(self):
        # Check which radio button is selected
        if self.radio_button_1.isChecked():
            # Perform action for option 1
            self.to_usd()
        elif self.radio_button_2.isChecked():
            # Perform action for option 2
            self.to_fbx()
                
                
    def to_usd(self):
        # check/remove for existing stage nodes
        export_node = "/stage/export_scene"
        import_node = "/stage/import_scene"
        text_input = self.textbox_temp.text()
        blender_input = self.textbox_blender.text()

        if hou.node(export_node):
           hou.node(export_node).destroy()
        
        if hou.node(import_node):
           hou.node(import_node).destroy()
        
        # create export nodes
        stage = hou.node("/stage")
        importNode = stage.createNode("sceneimport", "import_scene")
        exportNode = stage.createNode("usd_rop", "export_scene")
            
        # link import node to export node
        exportNode.setInput(0, importNode, 0)

        # set ouput path/file
        if self.selected_nodes:
            selected_output_nodes = [node.name() for node in self.selected_nodes]
            hou.parm("/stage/import_scene/forceobjects").set(" ".join(selected_output_nodes))
        else:
            hou.parm("/stage/import_scene/forceobjects").set("*")

        if self.checkbox_ani.isChecked():
            hou.parm("/stage/export_scene/trange").set(1)
            
        hou.parm("/stage/export_scene/lopoutput").set(text_input + "/temp_usd_scene.usd")

        # save usd file
        hou.parm("/stage/export_scene/execute").pressButton()
        
        # create a little python script for blender
        with open(text_input + "/import_usd.py", "w") as f:
            f.write("import bpy\n\n")
            f.write("usd_path = " + "\"" + text_input + "/temp_usd_scene.usd" + "\"\n\n")
            f.write("bpy.ops.wm.usd_import(filepath=usd_path)")

        # assign python file to blender
        usd_script = text_input + "/import_usd.py"

        blender_exe = blender_input + "/blender.exe"

        # blender commands
        cmd = [blender_exe, "--python", usd_script]

        # launch blender
        subprocess.Popen(cmd)

    def to_fbx(self):
        out = hou.node("/out")
        export_node = "/out/fbx_export"
        blender_input = self.textbox_blender.text()

        if hou.node(export_node):
           hou.node(export_node).destroy()

        # Set the file path for the FBX export
        output_path = temp_folder + "/temp_fbx_scene.fbx"
        text_input = self.textbox_temp.text()

        # Create an FBX export node
        export_node = out.createNode("filmboxfbx", "fbx_export")

        # Set the output path on the FBX export node
        hou.parm("/out/fbx_export/sopoutput").set(text_input + "/temp_fbx_scene.fbx")

        # set ouput path/file
        if self.selected_nodes:
            # Create a new bundle list object
            if hou.nodeBundle("selected_nodes"):
                hou.nodeBundle("selected_nodes").destroy()
                my_bundle_list = hou.addNodeBundle(name = "selected_nodes")
            else:    
                my_bundle_list = hou.addNodeBundle(name = "selected_nodes")

            # Add the selected nodes to the bundle
            for node in self.selected_nodes:
                my_bundle_list.addNode(node)

            hou.parm("/out/fbx_export/startnode").set("@selected_nodes")            
        else:
            hou.parm("/out/fbx_export/startnode").set("/obj")
        
        # Set the export options on the FBX export node
        hou.parm("/out/fbx_export/embedmedia").set(True)
        if self.checkbox_ani.isChecked():
            hou.parm("/out/fbx_export/trange").set(1)
        hou.parm("/out/fbx_export/exportkind").set(False)
        hou.parm("/out/fbx_export/convertunits").set(True)
        # hou.parm("/out/fbx_export/invisobj").set(3)
        hou.parm("/out/fbx_export/deformsasvcs").set(True)
        hou.parm("/out/fbx_export/forceskindeform").set(True)
        # hou.parm("/out/fbx_export/exportendeffectors").set(False)
        # hou.parm("/out/fbx_export/createsubnetroot").set(False)

        # Export the FBX file
        hou.parm("/out/fbx_export/execute").pressButton()
        
        # create a little python script for blender
        with open(text_input + "/import_fbx.py", "w") as f:
            f.write("import bpy\n\n")
            f.write("fbx_path = " + "\"" + text_input + "/temp_fbx_scene.fbx" + "\"\n\n")
            # f.write("bpy.ops.wm.read_homefile(use_empty=True)" + "\n\n")
            f.write("bpy.ops.import_scene.fbx(filepath=fbx_path)")

       # assign python file to blender
        fbx_script = text_input + "/import_fbx.py"
        blender_exe = blender_input + "/blender.exe"

        # blender commands
        cmd = [blender_exe, "--python", fbx_script]

        # launch blender
        subprocess.Popen(cmd)
        
    def customChecked(self, state):
        if self.checkbox_custom.isChecked():
            self.textbox_temp.setEnabled(True)
            self.btn_browse_temp.setEnabled(True)
        else:
            self.textbox_temp.setEnabled(False)
            self.btn_browse_temp.setEnabled(False)
            self.textbox_temp.setText(temp_folder)


    def blenderChecked(self, state):
        if self.checkbox_blender.isChecked():
            self.textbox_blender.setEnabled(True)
            self.btn_browse_blender.setEnabled(True)
        else:
            self.textbox_blender.setEnabled(False)
            self.btn_browse_blender.setEnabled(False)
            self.textbox_blender.setText(blender_folder)


    def onBrowseTemp(self, state):
        temp_folder = str(QFileDialog.getExistingDirectory(self, "Select new temporary folder"))
        self.textbox_temp.setText(temp_folder)

    def onBrowseBlender(self, state):
        blender_folder = str(QFileDialog.getExistingDirectory(self, "Select Blenders installation folder"))
        self.textbox_blender.setText(blender_folder)

        
# Create an instance of the window and show it
window = MyWindow()
window.show()
