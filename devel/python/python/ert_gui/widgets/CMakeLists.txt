set(PYTHON_SOURCES
    __init__.py
    active_label.py
    add_remove_widget.py
    button.py
    check_list.py
    checkbox.py
    cogwheel.py
    combo_choice.py
    double_box.py
    double_spinner.py
    help_dock.py
    helped_widget.py
    integer_spinner.py
    keyword_list.py
    keyword_table.py
    legend.py
    path_chooser.py
    path_format.py
    progress.py
    reloadbutton.py
    row_group.py
    row_panel.py
    search_box.py
    string_box.py
    tablewidgets.py
    util.py
    validated_dialog.py
    warning_panel.py
)

add_python_package("Python ert_gui.widgets"  ${PYTHON_INSTALL_PREFIX}/ert_gui/widgets "${PYTHON_SOURCES}" True)

