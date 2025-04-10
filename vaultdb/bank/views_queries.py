from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection

@api_view(['GET'])
def get_inactive_accounts(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.accountID, a.customer_id_id, a.balance, MAX(bt.timestamp) AS last_txn
            FROM bank_account a
            LEFT JOIN bank_banktransaction bt ON a.accountID = bt.account_id_id
            GROUP BY a.accountID, a.customer_id_id, a.balance
            HAVING MAX(bt.timestamp) < CURRENT_DATE - INTERVAL '2 months'
            ORDER BY last_txn;
        """)
        results = cursor.fetchall()
    return Response(results)
