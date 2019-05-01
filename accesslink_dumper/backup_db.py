import sh
from utils import load_config

config = load_config("config.yml")

print("Dumping DB to dump/ directory")
sh.mongodump(
        authenticationDatabase="admin",
        db=config["mongo_db"],
        username=config["mongo_user"],
        password=config["mongo_pass"])

print("Removing existing backup archive (if any)")
sh.rm("-f", "backup.tar.gz")

print("Compressing backup directory to backup.tar.gz")
sh.tar("zcvf", "backup.tar.gz", "dump/")
