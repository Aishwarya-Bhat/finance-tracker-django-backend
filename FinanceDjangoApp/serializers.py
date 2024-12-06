from rest_framework import serializers

class ExpenseSerializer(serializers.Serializer):
    expenseID = serializers.CharField(required=False)
    payeeDetail = serializers.CharField(max_length=200)
    remarks = serializers.CharField(required=False, allow_blank=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    budgetID = serializers.CharField(max_length=15)
    categoryID = serializers.IntegerField()
    date = serializers.DateField()


class BudgetSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField(min_value=1, max_value=12)
    budgetAmount = serializers.DecimalField(max_digits=10, decimal_places=2)

#     from rest_framework import serializers
# from .models import Category, Expense

# class ExpenseSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Expense
#         exclude = ['category']  # Exclude categoryID

# class CategorySerializer(serializers.ModelSerializer):
#     expenses = ExpenseSerializer(many=True)

#     class Meta:
#         model = Category
#         fields = ['categoryName', 'expenses']


