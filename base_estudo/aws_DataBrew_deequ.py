# AWS Glue DataBrew (similar)
# Deequ no Spark
from pydeequ.checks import *
from pydeequ.verification import *

check = Check(spark, CheckLevel.Warning, "Fraud Data Quality")
checkResult = VerificationSuite(spark) \
    .onData(df) \
    .addCheck(
        check.hasSize(lambda x: x >= 1000) \
        .isComplete("transaction_id") \
        .isUnique("transaction_id") \
        .isComplete("amount") \
        .isNonNegative("amount")
    ) \
    .run()