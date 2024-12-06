from django.shortcuts import render

# Create your views here.
from django.db import connection
from django.http import JsonResponse
from .models import Source
from datetime import date
from .serializers import ExpenseSerializer
from datetime import datetime


def fetch_activity(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Activity")
        rows = cursor.fetchall()
    
    data = [
        {"activityID": row[0], "activityType": row[1], "userID": row[2]}
        for row in rows
    ]
    return JsonResponse(data, safe=False)


def add_expense(request):
    return JsonResponse({"message": "Expense added successfully"})




from django.shortcuts import render
from django.db import connection
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .IncomeSerializer import IncomeSerializer
from datetime import date
import re

class IncomeView(APIView):
    def post(self, request):
        # Log incoming data
        print("Request data:", request.data)

        # Extract data from request
        payerDetail = request.data.get("payerDetail")
        remarks = request.data.get("remarks")
        amount = request.data.get("amount")
        sourceID = request.data.get("sourceID")

        # Validate required fields
        if not payerDetail or not amount or not sourceID:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate the next incomeID
        with connection.cursor() as cursor:
            cursor.execute("SELECT incomeID FROM Income ORDER BY incomeID DESC LIMIT 1;")
            result = cursor.fetchone()
            if result:
                match = re.match(r"I(\d+)", result[0])
                next_id = int(match.group(1)) + 1 if match else 1
            else:
                next_id = 1
        incomeID = f"I{next_id}"

        # Auto-generate other fields
        activityID = "A1"  # Hardcoded for Income
        incomeDate = date.today()

        # Construct and execute the raw SQL query
        raw_query = """
        INSERT INTO Income (incomeID, payerDetail, remarks, amount, activityID, incomeDate, sourceID)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        values = (
            incomeID,
            payerDetail,
            remarks,
            amount,
            activityID,
            incomeDate,
            sourceID,
        )

        try:
            with connection.cursor() as cursor:
                cursor.execute(raw_query, values)
        except Exception as e:
            print("Database error:", e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Income record created successfully!", "incomeID": incomeID}, status=status.HTTP_201_CREATED)


class ExpenseView(APIView):
    def post(self, request):
        try:
            serializer = ExpenseSerializer(data=request.data)
            if serializer.is_valid():
                data = serializer.validated_data

                # First, check if the budgetID exists
                check_budget_query = "SELECT COUNT(*) FROM Budget WHERE budgetID = %s"
                with connection.cursor() as cursor:
                    cursor.execute(check_budget_query, [data['budgetID']])
                    if cursor.fetchone()[0] == 0:
                        return Response(
                            {"error": f"Budget with ID {data['budgetID']} does not exist"},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                # Check if the categoryID exists
                check_category_query = "SELECT COUNT(*) FROM Category WHERE categoryID = %s"
                with connection.cursor() as cursor:
                    cursor.execute(check_category_query, [data['categoryID']])
                    if cursor.fetchone()[0] == 0:
                        return Response(
                            {"error": f"Category with ID {data['categoryID']} does not exist"},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                # Modified query to get the highest numeric value from expenseID
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT CAST(SUBSTRING(expenseID, 2) AS UNSIGNED) as numeric_id 
                        FROM Expense 
                        WHERE expenseID REGEXP '^E[0-9]+$'
                        ORDER BY numeric_id DESC 
                        LIMIT 1;
                    """)
                    result = cursor.fetchone()
                    next_id = (result[0] + 1) if result and result[0] else 1
                    expenseID = f"E{next_id}"

                # Set fixed activityID for Expense
                activityID = "A2"
                
                # Parse and format the date properly
                expense_date = data['date']
                if isinstance(expense_date, str):
                    expense_date = datetime.strptime(expense_date, '%Y-%m-%d').date()
                
                print(f"Received date: {expense_date}")  # Debug log

                # Check if the date exists in the Date table
                check_date_query = "SELECT COUNT(*) FROM Date WHERE date = %s"
                with connection.cursor() as cursor:
                    cursor.execute(check_date_query, [expense_date])
                    if cursor.fetchone()[0] == 0:
                        # Insert the date if it doesn't exist
                        insert_date_query = "INSERT INTO Date (date) VALUES (%s)"
                        cursor.execute(insert_date_query, [expense_date])

                # Construct the raw SQL query
                raw_query = """
                INSERT INTO Expense (
                    expenseID, payeeDetail, remarks, amount, 
                    budgetID, activityID, date, categoryID
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """
                values = (
                    expenseID,
                    data['payeeDetail'],
                    data.get('remarks', ''),
                    data['amount'],
                    data['budgetID'],
                    activityID,
                    expense_date,
                    data['categoryID']
                )

                with connection.cursor() as cursor:
                    cursor.execute(raw_query, values)
                    print(f"Inserted date: {expense_date}")  # Debug log

                return Response({
                    "message": "Expense added successfully",
                    "expenseID": expenseID
                }, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Error processing expense: {str(e)}")  # Debug log
            return Response({
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




from django.shortcuts import render
from django.db import connection
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import date


class BudgetView(APIView):
    def post(self, request):
        try:
            # Extract data from request
            year = request.data.get('year')
            month = request.data.get('month')
            budget_amount = request.data.get('budgetAmount')

            if not year or not month or not budget_amount:
                return Response(
                    {"error": "Year, month, and budgetAmount are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate year and month
            if not (1 <= month <= 12):
                return Response({"error": "Month must be between 1 and 12."}, status=status.HTTP_400_BAD_REQUEST)

            if year < 1900 or year > 2100:
                return Response({"error": "Year must be valid."}, status=status.HTTP_400_BAD_REQUEST)

            # Generate budgetID
            budgetID = f"B{month:02d}{year}"  # Format month as 2 digits (e.g., B022023)

            # Fixed userID (as specified in requirements)
            userID = "U1"

            # Insert into the database using a raw SQL query
            raw_query = """
            INSERT INTO Budget (budgetID, year, month, budgetAmount, userID)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE budgetAmount = VALUES(budgetAmount);
            """
            values = (budgetID, year, month, budget_amount, userID)

            with connection.cursor() as cursor:
                cursor.execute(raw_query, values)

            return Response({"message": "Budget record created successfully!", "budgetID": budgetID}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#--------------------------------
# Fetch all budgets

from django.db import connection
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class BudgetListView(APIView):
    def get(self, request):
        try:
            # Query to fetch all budgets ordered by most recent first
            # Returns: Complete budget information including ID, year, month, and amount
            raw_query = """
            SELECT 
                budgetID,       -- Unique identifier for each budget
                year,           -- Budget year
                month,          -- Budget month
                budgetAmount    -- Allocated budget amount
            FROM Budget
            ORDER BY year DESC, month DESC;  -- Most recent budgets first
            """

            with connection.cursor() as cursor:
                cursor.execute(raw_query)
                rows = cursor.fetchall()

            # Updated dictionary to include budgetID
            budgets = [
                {
                    "budgetID": row[0],
                    "year": row[1], 
                    "month": row[2], 
                    "budgetAmount": float(row[3])
                }
                for row in rows
            ]

            return Response(budgets, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from django.db import connection
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class BudgetUpdateView(APIView):
    def post(self, request, budget_id):
        try:
            data = request.data
            # Query to update existing budget record
            # Updates year, month, and budgetAmount for the specified budgetID
            raw_query = """
            UPDATE Budget
            SET year = %s,           -- Year of the budget
                month = %s,          -- Month number (1-12)
                budgetAmount = %s    -- New budget amount
            WHERE budgetID = %s;     -- Target budget to update
            """
            with connection.cursor() as cursor:
                cursor.execute(raw_query, [data['year'], data['month'], data['budgetAmount'], budget_id])

            return Response({"message": "Budget updated successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BudgetDeleteView(APIView):
    def post(self, request, budget_id):
        # Query to delete a specific budget record
        # Cascading delete will remove related records in other tables
        raw_query = """
        DELETE FROM Budget
        WHERE budgetID = %s;  -- Target budget to delete
        """
        with connection.cursor() as cursor:
            cursor.execute(raw_query, [budget_id])

        return Response({"message": "Budget deleted successfully."}, status=status.HTTP_200_OK)

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from .models import Category
# from .serializers import CategorySerializer

# class ExpenseListView(APIView):
#     def get(self, request):
#         categories = Category.objects.prefetch_related('expenses').all()
#         serializer = CategorySerializer(categories, many=True)
#         return Response(serializer.data)


class ExpenseListView(APIView):
    def get(self, request):
        try:
            # Query to fetch all categories for the dropdown menu
            # Returns: categoryID and categoryName sorted alphabetically
            categories_query = """
            SELECT categoryID, categoryName 
            FROM Category 
            ORDER BY categoryName;
            """
            
            # Query to fetch all expenses with their category details
            # Performs a LEFT JOIN to include categories even if they have no expenses
            # Returns: combined category and expense information
            expenses_query = """
            SELECT 
                c.categoryID,
                c.categoryName,
                e.expenseID,
                e.payeeDetail,
                e.remarks,
                e.amount,
                e.budgetID,
                e.date
            FROM Category c
            LEFT JOIN Expense e ON c.categoryID = e.categoryID
            ORDER BY c.categoryName, e.date DESC;
            """

            with connection.cursor() as cursor:
                # Get categories for dropdown
                cursor.execute(categories_query)
                categories = [
                    {"categoryID": row[0], "categoryName": row[1]}
                    for row in cursor.fetchall()
                ]

                # Get expenses
                cursor.execute(expenses_query)
                rows = cursor.fetchall()

            # Process the results to group by category
            categories_with_expenses = {}
            for row in rows:
                category_id = row[0]
                category_name = row[1]
                
                if row[2]:  # If there are expenses for this category
                    expense = {
                        'expenseID': row[2],
                        'payeeDetail': row[3],
                        'remarks': row[4],
                        'amount': float(row[5]) if row[5] else 0,
                        'budgetID': row[6],
                        'date': row[7].strftime('%Y-%m-%d') if row[7] else None
                    }
                    
                    if category_name not in categories_with_expenses:
                        categories_with_expenses[category_name] = {
                            'categoryID': category_id,
                            'categoryName': category_name,
                            'expenses': []
                        }
                    
                    categories_with_expenses[category_name]['expenses'].append(expense)

            # Make sure all categories are included, even those without expenses
            for category in categories:
                category_name = category['categoryName']
                if category_name not in categories_with_expenses:
                    categories_with_expenses[category_name] = {
                        'categoryID': category['categoryID'],
                        'categoryName': category_name,
                        'expenses': []
                    }

            return Response({
                'categories': categories,
                'categoryExpenses': list(categories_with_expenses.values())
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error fetching expenses: {str(e)}")  # Add debug logging
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExpenseUpdateView(APIView):
    def post(self, request, expense_id):
        try:
            data = request.data
            # Query to update existing expense record
            # Updates payee details, remarks, amount, and date
            raw_query = """
            UPDATE Expense
            SET payeeDetail = %s,    -- Who was paid
                remarks = %s,        -- Additional notes
                amount = %s,         -- Updated expense amount
                date = %s           -- When expense occurred
            WHERE expenseID = %s;    -- Target expense to update
            """
            values = [
                data['payeeDetail'],
                data['remarks'],
                data['amount'],
                data['date'],
                expense_id
            ]

            with connection.cursor() as cursor:
                cursor.execute(raw_query, values)
            
            return Response({"message": "Expense updated successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ExpenseDeleteView(APIView):
    def post(self, request, expense_id):
        try:
            # Query to delete a specific expense record
            # Cascading delete will remove related records
            raw_query = "DELETE FROM Expense WHERE expenseID = %s;"
            with connection.cursor() as cursor:
                cursor.execute(raw_query, [expense_id])
            
            return Response({"message": "Expense deleted successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IncomeListView(APIView):
    def get(self, request):
        try:
            # Query to fetch all income sources for the dropdown menu
            # Returns: sourceID and sourceName sorted alphabetically
            sources_query = """
            SELECT sourceID, sourceName 
            FROM Source 
            ORDER BY sourceName;
            """
            
            # Query to fetch all incomes with their source details
            # Performs a LEFT JOIN to include sources even if they have no incomes
            # Returns: combined source and income information
            incomes_query = """
            SELECT 
                s.sourceName,
                s.sourceID,
                i.incomeID,
                i.payerDetail,
                i.remarks,
                i.amount,
                i.incomeDate
            FROM Source s
            LEFT JOIN Income i ON s.sourceID = i.sourceID
            ORDER BY s.sourceName, i.incomeDate DESC;
            """

            with connection.cursor() as cursor:
                # Get sources for dropdown
                cursor.execute(sources_query)
                sources = [
                    {"sourceID": row[0], "sourceName": row[1]}
                    for row in cursor.fetchall()
                ]

                # Get incomes
                cursor.execute(incomes_query)
                rows = cursor.fetchall()

            # Process the results to group by source
            sources_with_incomes = {}
            for row in rows:
                source_name = row[0]
                source_id = row[1]
                
                if row[3]:  # If there are incomes for this source
                    income = {
                        'incomeID': row[2],      # Add incomeID
                        'payerDetail': row[3],
                        'remarks': row[4],
                        'amount': float(row[5]) if row[5] else 0,
                        'incomeDate': row[6].strftime('%Y-%m-%d') if row[6] else None
                    }
                else:
                    continue

                if source_name not in sources_with_incomes:
                    sources_with_incomes[source_name] = {
                        'sourceID': source_id,
                        'sourceName': source_name,
                        'incomes': []
                    }
                
                sources_with_incomes[source_name]['incomes'].append(income)

            return Response({
                'sources': sources,
                'sourceIncomes': list(sources_with_incomes.values())
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class IncomeUpdateView(APIView):
    def post(self, request, income_id):
        try:
            data = request.data
            print(f"Updating income {income_id} with data:", data)  # Debug log

            # Query to check if income record exists
            # Returns count of matching records
            check_income_query = """
            SELECT COUNT(*) 
            FROM Income 
            WHERE incomeID = %s;     -- Income record to verify
            """

            # Query to check if date exists in Date table
            # Returns count of matching dates
            check_date_query = """
            SELECT COUNT(*) 
            FROM Date 
            WHERE date = %s;         -- Date to verify
            """

            # Query to insert new date if it doesn't exist
            insert_date_query = """
            INSERT INTO Date (date) 
            VALUES (%s);             -- New date to add
            """

            # Query to update existing income record
            # Updates all modifiable fields for the income
            raw_query = """
            UPDATE Income
            SET payerDetail = %s,
                remarks = %s,
                amount = %s,
                incomeDate = %s
            WHERE incomeID = %s;
            """
            values = [
                data['payerDetail'],
                data.get('remarks', ''),
                data['amount'],
                data['incomeDate'],
                income_id
            ]

            with connection.cursor() as cursor:
                cursor.execute(check_income_query, [income_id])
                if cursor.fetchone()[0] == 0:
                    return Response(
                        {"error": f"Income with ID {income_id} does not exist"},
                        status=status.HTTP_404_NOT_FOUND
                    )

                cursor.execute(check_date_query, [data['incomeDate']])
                if cursor.fetchone()[0] == 0:
                    # Insert the date if it doesn't exist
                    cursor.execute(insert_date_query, [data['incomeDate']])

                cursor.execute(raw_query, values)
            
            return Response({
                "message": "Income updated successfully",
                "incomeID": income_id
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error updating income: {str(e)}")  # Debug log
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class IncomeDeleteView(APIView):
    def post(self, request, income_id):
        try:
            # Query to delete a specific income record
            # Cascading delete will remove related records
            raw_query = """
            DELETE FROM Income 
            WHERE incomeID = %s;
            """
            with connection.cursor() as cursor:
                cursor.execute(raw_query, [income_id])
            
            return Response({"message": "Income deleted successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AuditLogView(APIView):
    def get(self, request):
        try:
            # Query to fetch audit log entries ordered by most recent first
            # This query excludes logID and recordID for security and displays only necessary information
            # Returns: actionType (INSERT/UPDATE/DELETE), tableName, actionDate, and operation details
            query = """
            SELECT 
                actionType,    -- Type of operation performed (INSERT/UPDATE/DELETE)
                tableName,     -- Name of the table where operation was performed
                actionDate,    -- Timestamp when the operation occurred
                details       -- JSON string containing operation details
            FROM AuditLog
            ORDER BY actionDate DESC;  -- Most recent actions first
            """

            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()

            audit_logs = [
                {
                    'actionType': row[0],
                    'tableName': row[1],
                    'actionDate': row[2].strftime('%Y-%m-%d %H:%M:%S'),
                    'details': row[3]
                }
                for row in rows
            ]

            return Response(audit_logs, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MonthlyIncomeView(APIView):
    def get(self, request):
        try:
            month = request.GET.get('month')
            year = request.GET.get('year')
            
            with connection.cursor() as cursor:
                cursor.callproc('GetMonthlyIncomeByMonthYear', [int(month), int(year)])
                result = cursor.fetchone()
                print(f"Stored procedure Income result.......: {result}")
                
                # Get the first element (index 0) which contains the total
                monthly_total = float(result[2]) if result and result[0] is not None else 0.0
                print(f"Monthly Income total.......: {monthly_total}")
                
                return Response({
                    'monthlyTotal': monthly_total,
                    'month': month,
                    'year': year
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            print(f"Income Error: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MonthlyExpenseView(APIView):
    def get(self, request):
        try:
            month = request.GET.get('month')
            year = request.GET.get('year')
            
            if not month or not year:
                return Response(
                    {"error": "Month and year are required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            with connection.cursor() as cursor:
                try:
                    cursor.callproc('GetMonthlyExpenseByMonthYear', [int(month), int(year)])
                    result = cursor.fetchone()
                    print(f"Stored procedure Expense result.......: {result}")
                    
                    # Get the first element (index 0) which contains the total
                    monthly_total = float(result[2]) if result and result[0] is not None else 0.0
                    print(f"Monthly Expense total.......: {monthly_total}")
                    
                    return Response({
                        'monthlyTotal': monthly_total,
                        'month': month,
                        'year': year
                    }, status=status.HTTP_200_OK)
                    
                except Exception as db_error:
                    print(f"Database error: {str(db_error)}")
                    return Response(
                        {"error": f"Database error: {str(db_error)}"}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
        except Exception as e:
            print(f"General error: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

