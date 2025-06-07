import sys
import yaml
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt

from site_discovery.core import discover_sites
from utils import db, export, dedup, auth
from scheduler import scheduler


def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    config = load_config()
    db.init_db()
    app = QtWidgets.QApplication(sys.argv)
    window = uic.loadUi("gui/discovery.ui")

    def refresh_sites():
        method = "google"
        if window.radioBing.isChecked():
            method = "bing"
        elif window.radioCustom.isChecked():
            method = "custom"
        keywords_text = window.editKeywords.toPlainText()
        keywords = [k.strip() for k in keywords_text.split(",") if k.strip()]
        results = discover_sites(method, keywords)
        window.tableResults.setRowCount(len(results))
        for i, r in enumerate(results):
            window.tableResults.setItem(i, 0, QtWidgets.QTableWidgetItem(str(i + 1)))
            window.tableResults.setItem(i, 1, QtWidgets.QTableWidgetItem(r.get("name", "")))
            window.tableResults.setItem(i, 2, QtWidgets.QTableWidgetItem(r.get("url", "")))

    window.btnDiscover.clicked.connect(refresh_sites)
    window.btnRefreshSites.clicked.connect(refresh_sites)

    def manage_creds():
        row = window.tableResults.currentRow()
        if row < 0:
            return
        site_name = window.tableResults.item(row, 1).text()
        dlg = uic.loadUi("gui/login.ui")

        def save():
            user = dlg.editUsername.text()
            pwd = dlg.editPassword.text()
            master, ok = QtWidgets.QInputDialog.getText(dlg, "Master", "كلمة المرور الرئيسية", QtWidgets.QLineEdit.Password)
            if not ok:
                return
            auth.save_credentials(site_name, user, pwd, master)
            dlg.accept()

        dlg.btnSave.clicked.connect(save)
        dlg.btnCancel.clicked.connect(dlg.reject)
        dlg.exec_()

    window.btnManageCreds.clicked.connect(manage_creds)

    def open_scheduler():
        sched_win = uic.loadUi("gui/scheduler.ui")

        def refresh_jobs():
            jobs = scheduler.list_jobs()
            sched_win.tableJobs.setRowCount(len(jobs))
            for i, job in enumerate(jobs):
                sched_win.tableJobs.setItem(i, 0, QtWidgets.QTableWidgetItem(job.id))
                sched_win.tableJobs.setItem(i, 1, QtWidgets.QTableWidgetItem(str(job.trigger)))

        def add_job():
            cron = sched_win.editCron.text() or config["scheduling"]["default_cron"]
            scheduler.add_job(scrape_all, cron, job_id=f"job_{len(scheduler.list_jobs())+1}")
            refresh_jobs()

        def remove_job():
            row = sched_win.tableJobs.currentRow()
            if row < 0:
                return
            job_id = sched_win.tableJobs.item(row, 0).text()
            scheduler.remove_job(job_id)
            refresh_jobs()

        sched_win.btnAdd.clicked.connect(add_job)
        sched_win.btnRemove.clicked.connect(remove_job)
        sched_win.btnStart.clicked.connect(scheduler.start)
        sched_win.btnStop.clicked.connect(scheduler.stop)

        refresh_jobs()
        sched_win.show()

    window.btnScheduler.clicked.connect(open_scheduler)

    def scrape_all():
        scraper_win = uic.loadUi("gui/scraper.ui")

        def start_scrape():
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
                master_password, ok = QtWidgets.QInputDialog.getText(scraper_win, "Master", "كلمة المرور الرئيسية", QtWidgets.QLineEdit.Password)
                if not ok:
                    return

            selected_sites = []
            for i in range(window.tableResults.rowCount()):
                if window.tableResults.item(i, 0).isSelected() or window.tableResults.item(i, 1).isSelected():
                    selected_sites.append(window.tableResults.item(i, 1).text())

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

        scraper_win.btnStartScrape.clicked.connect(start_scrape)
        scraper_win.show()


    window.btnOpenScraper.clicked.connect(scrape_all)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
