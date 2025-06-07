import sys
import yaml
from PyQt5 import QtWidgets, uic

from site_discovery.core import discover_sites


def load_config(path="config.yaml"):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def main():
    config = load_config()
    app = QtWidgets.QApplication(sys.argv)
    window = uic.loadUi('gui/discovery.ui')

    def on_discover():
        method = 'google'
        if window.radioBing.isChecked():
            method = 'bing'
        elif window.radioCustom.isChecked():
            method = 'custom'
        keywords_text = window.editKeywords.toPlainText()
        keywords = [k.strip() for k in keywords_text.split(',') if k.strip()]
        results = discover_sites(method, keywords)
        window.tableResults.setRowCount(len(results))
        for i, r in enumerate(results):
            window.tableResults.setItem(i, 0, QtWidgets.QTableWidgetItem(str(i+1)))
            window.tableResults.setItem(i, 1, QtWidgets.QTableWidgetItem(r.get('name','')))
            window.tableResults.setItem(i, 2, QtWidgets.QTableWidgetItem(r.get('url','')))

    window.btnDiscover.clicked.connect(on_discover)

    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
