import sys
import os
import yaml
from PyQt5 import QtWidgets, uic

from site_discovery.core import discover_sites
from utils import db, export, dedup, auth
from scheduler import scheduler


def load_config(path: str | None = None):
    """Load configuration from YAML file."""
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    config = load_config()
    db.init_db()
    app = QtWidgets.QApplication(sys.argv)
    font = app.font()
    font.setPointSize(14)
    app.setFont(font)

    window = uic.loadUi("gui/mainwindow.ui")
    stack = window.findChild(QtWidgets.QStackedWidget, "stackedWidget")
    nav = window.findChild(QtWidgets.QListWidget, "listNavigation")

    pageDiscovery = uic.loadUi("gui/page_discovery.ui")
    pageLogin = uic.loadUi("gui/page_login.ui")
    pageScraper = uic.loadUi("gui/page_scraper.ui")
    pageScheduler = uic.loadUi("gui/page_scheduler.ui")
    stack.addWidget(pageDiscovery)
    stack.addWidget(pageLogin)
    stack.addWidget(pageScraper)
    stack.addWidget(pageScheduler)
    nav.currentRowChanged.connect(stack.setCurrentIndex)

    def refresh_sites():
        method = "google"
        if pageDiscovery.radioBing.isChecked():
            method = "bing"
        elif pageDiscovery.radioCustom.isChecked():
            method = "custom"
        keywords_text = pageDiscovery.editKeywords.toPlainText()
        keywords = [k.strip() for k in keywords_text.split(",") if k.strip()]
        results = discover_sites(method, keywords)
        pageDiscovery.tableResults.setRowCount(len(results))
        for i, r in enumerate(results):
            pageDiscovery.tableResults.setItem(i, 0, QtWidgets.QTableWidgetItem(str(i + 1)))
            pageDiscovery.tableResults.setItem(i, 1, QtWidgets.QTableWidgetItem(r.get("name", "")))
            pageDiscovery.tableResults.setItem(i, 2, QtWidgets.QTableWidgetItem(r.get("url", "")))

    pageDiscovery.btnDiscover.clicked.connect(refresh_sites)
    pageDiscovery.btnRefreshSites.clicked.connect(refresh_sites)

    def manage_creds():
        row = pageDiscovery.tableResults.currentRow()
        if row < 0:
            return
        site_name = pageDiscovery.tableResults.item(row, 1).text()

        try:
            pageLogin.btnSave.clicked.disconnect()
            pageLogin.btnCancel.clicked.disconnect()
        except Exception:
            pass

        def save():
            user = pageLogin.editUsername.text()
            pwd = pageLogin.editPassword.text()
            master, ok = QtWidgets.QInputDialog.getText(window, "Master", "كلمة المرور الرئيسية", QtWidgets.QLineEdit.Password)
            if not ok:
                return
            auth.save_credentials(site_name, user, pwd, master)
            nav.setCurrentRow(0)

        pageLogin.btnSave.clicked.connect(save)
        pageLogin.btnCancel.clicked.connect(lambda: nav.setCurrentRow(0))
        nav.setCurrentRow(1)

    pageDiscovery.btnManageCreds.clicked.connect(manage_creds)

    def open_scheduler():
        try:
            pageScheduler.btnAdd.clicked.disconnect()
            pageScheduler.btnRemove.clicked.disconnect()
            pageScheduler.btnStart.clicked.disconnect()
            pageScheduler.btnStop.clicked.disconnect()
        except Exception:
            pass

        def refresh_jobs():
            jobs = scheduler.list_jobs()
            pageScheduler.tableJobs.setRowCount(len(jobs))
            for i, job in enumerate(jobs):
                pageScheduler.tableJobs.setItem(i, 0, QtWidgets.QTableWidgetItem(job.id))
                pageScheduler.tableJobs.setItem(i, 1, QtWidgets.QTableWidgetItem(str(job.trigger)))

        def add_job():
            cron = pageScheduler.editCron.text() or config["scheduling"]["default_cron"]
            scheduler.add_job(scrape_all, cron, job_id=f"job_{len(scheduler.list_jobs())+1}")
            refresh_jobs()

        def remove_job():
            row = pageScheduler.tableJobs.currentRow()
            if row < 0:
                return
            job_id = pageScheduler.tableJobs.item(row, 0).text()
            scheduler.remove_job(job_id)
            refresh_jobs()

        pageScheduler.btnAdd.clicked.connect(add_job)
        pageScheduler.btnRemove.clicked.connect(remove_job)
        pageScheduler.btnStart.clicked.connect(scheduler.start)
        pageScheduler.btnStop.clicked.connect(scheduler.stop)

        refresh_jobs()
        nav.setCurrentRow(3)

    pageDiscovery.btnScheduler.clicked.connect(open_scheduler)

    def scrape_all():
        scraper_win = pageScraper
        selected_fields = []
        if scraper_win.checkTitle.isChecked():
            selected_fields.append("title")
        if scraper_win.checkPrice.isChecked():
            selected_fields.append("price")
        if scraper_win.checkDescription.isChecked():
            selected_fields.append("description")
        if scraper_win.checkLocation.isChecked():
            selected_fields.append("location")
        if scraper_win.checkImages.isChecked():
            selected_fields.append("images")
        if scraper_win.checkPhone.isChecked():
            selected_fields.append("phone")

        save_path = scraper_win.editSavePath.text() or config["storage"]["images"]
        proxy = config.get("network", {}).get("proxy")
        master_password = ""
        if config.get("authentication", {}).get("use_master_password"):
            master_password, ok = QtWidgets.QInputDialog.getText(window, "Master", "كلمة المرور الرئيسية", QtWidgets.QLineEdit.Password)
            if not ok:
                return

        selected_sites = []
        for i in range(pageDiscovery.tableResults.rowCount()):
            if pageDiscovery.tableResults.item(i, 0).isSelected() or pageDiscovery.tableResults.item(i, 1).isSelected():
                selected_sites.append(pageDiscovery.tableResults.item(i, 1).text())

        results_count = 0
        total = len(selected_sites)
        for idx, site_name in enumerate(selected_sites, 1):
            try:
                module = __import__(f"site_scrapers.plugins.{site_name}", fromlist=["scrape"])
            except ImportError:
                continue
            creds = auth.load_credentials(site_name, master_password) if master_password else None
            listings = module.scrape(fields=selected_fields, save_path=save_path, credentials=creds, proxy=proxy)
            with db.SessionLocal() as session:
                unique = dedup.dedup_listings(session, listings)
                for lst in unique:
                    db.save_listing(session, site_name, lst)
            export.export_csv(listings, f"{site_name}.csv")
            export.export_json(listings, f"{site_name}.json")
            results_count += len(listings)
            scraper_win.progressBar.setValue(int(idx / total * 100))

        if sys.platform.startswith("win") and config.get("notifications", {}).get("toast"):
            from win10toast import ToastNotifier

            toaster = ToastNotifier()
            toaster.show_toast("اكتمال التجريف", f"تم استخراج {results_count} اعلان", threaded=True)


    pageScraper.btnStartScrape.clicked.connect(scrape_all)
    pageDiscovery.btnOpenScraper.clicked.connect(lambda: nav.setCurrentRow(2))
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
